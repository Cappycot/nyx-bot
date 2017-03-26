# HTML scraper for Unison League news

import asyncio
from datetime import datetime
import discord
from html.parser import HTMLParser
from sys import exc_info
import urllib3


################################################################################
# Main/Global Variables
################################################################################

http = urllib3.PoolManager()
languages = [["de", ["de", "ge"]], ["en", ["en"]], ["es", ["es", "sp"]],
            ["fr", ["fr"]], ["it", ["it"]], ["pt", ["por", "pt"]]]
# Datetime stamp for next or previous maintenance
maintenance = None
# Form: [[title, id number, datetime, temp url],...]
notices = []
updated = None
updated_string = ""
# http://app.en.unisonleague.com/app_en/information.php?action_information_index=true&lang=en&past=1
# url_main = "http://app.en.unisonleague.com/app_en/information.php?&lang=en"
url_main = "http://app.en.unisonleague.com/app_en/information.php?action_information_index=true&lang="

# http://app.en.unisonleague.com/app_en/information.php?action_information_detail=true&information_id=984&user_id=0&callback=information_index&row=1&lang=en
url_side1 = "http://app.en.unisonleague.com/app_en/information.php?action_information_detail=true&information_id="
url_side2 = "&user_id=0&callback=information_index&row="
# http://app.en.unisonleague.com/app_en/information.php?action_information_detail=true&information_id=984&user_id=0&callback=information_index&row=1&lang=en

################################################################################
# Parser Classes
################################################################################

class EventPageParser(HTMLParser):
    max_lines = 10
    def __init__(self, HTMLParser):
        HTMLParser.__init__(self)
        self.date = ""
        self.div_text = False
        self.get_date = False
        self.get_text = 0
        self.get_title = False
        self.image = None
        self.maintenance = None
        self.max_text = False
        self.text = ""
        self.text_lines = 0
        self.title = ""       
    
    def handle_starttag(self, tag, attrs):
        self.get_title = not self.title and tag == "div" and attrs[0][1] == "detail_title_word"
        if tag == "br" and self.text_lines < EventPageParser.max_lines and self.text[-1:] != "\n":
            self.text += "\n"
        elif tag == "img" and self.image is None:
            for attr in attrs:
                if attr[0] == "src":
                    self.image = attr[1].replace("\n", "").replace("\r", "").strip()
                elif attr[0] == "class":
                    if attr[1] == "detail_back_img":
                        self.image = None
                        break
        elif tag == "div" and attrs[0][1] == "tv":
            self.get_date = True
        elif tag == "div" and attrs[0][1] == "detail_body_word" or tag == "p" or tag == "span":
            if not self.div_text:
                self.div_text = True
            if self.text_lines < EventPageParser.max_lines:
                self.get_text += 1
            elif not self.max_text:
                self.max_text = True
                self.text += "..."
    
    def handle_data(self, data):
        if self.get_date:
            self.date = ": " + data.replace("\n", "").replace("\r", "").strip()
            self.get_date = False
        elif self.get_text > 0:
            self.text += self.trim(data) # data.replace("\n", "").replace("\r", "")
        elif self.get_title:
            self.title = data.replace("\n", "").replace("\r", "").strip()
            self.get_title = False
    
    def handle_endtag(self, tag):
        if (tag == "div" and self.div_text or tag == "p" or tag == "span") and self.get_text > 0:
            self.get_text -= 1
            if tag == "div":
                self.get_text = 0
            if (self.get_text == 0 or tag == "p") and self.text[-1:] != "\n":
                self.text += "\n"
            self.text_lines += 1
            if self.text_lines == EventPageParser.max_lines:
                self.get_text = 0
    
    def trim(self, text = None):
        if text is None:
            text = self.text
        while text[:1] == "\n" or text[:1] == "\r":
            text = text[1:]
        while text[-1:] == "\n" or text[-1:] == "\r" or text[-4:] == "....":
            text = text[:-1]
        return text
        

# r = http.request("GET", "http://app.en.unisonleague.com/app_en/information.php?action_information_detail=true&information_id=670&callback=information_index&lang=en")
# asdf = r.data.decode("utf-8")
# parser = EventPageParser(HTMLParser)
# parser.feed(asdf)
# print("Title:")
# print(parser.title)
# print("\nImage:")
# print(parser.image)
# print("\nBody:\n")
# parser.text = parser.trim()
# print(parser.text)
# print("\nEnd of Body")


class MainPageParser(HTMLParser):
    # Super init then set vars
    def __init__(self, HTMLParser, lang="en"):
        HTMLParser.__init__(self)
        self.get_date = False
        self.get_time = False
        self.lang = lang
        self.notice = None
    
    def handle_starttag(self, tag, attrs):
        # print("Start of tag", tag)
        # print(attrs)
        global notices
        if tag == "a":
            if not self.notice is None:
                notices.append(self.notice)
                # print(self.notice)
            url = attrs[0][1]
            if url_side1 in url and url_side2 in url:
                id_start = url.index(url_side1) + len(url_side1)
                # print("start found")
                id_end = url.index(url_side2)
                # print("end found")
                id_num = url[id_start:id_end]
                event_url = url_side1 + id_num + url_side2 + "1&lang=" + self.lang
                # print(event_url)
                event_data = http.request("GET", event_url).data.decode("UTF-8")
                # print("send to parser")
                e_parser = EventPageParser(HTMLParser)
                e_parser.feed(event_data)
                self.notice = [e_parser.title, int(id_num), None, event_url]
                # print("keep on going")
            else:
                self.notice = None
        elif tag == "div":
            dclass = attrs[0][1]
            if dclass == "current_time":
                self.get_time = True
            elif dclass == "tv":
                self.get_date = True
            elif dclass.startswith("category--"):
                self.get_category = True
    
    def handle_data(self, data):
        global updated_string
        data = data.replace("\n", "").strip()
        if data:
            if self.get_time:
                updated_string = data
                self.get_time = False
            elif self.get_date:
                cal = data.split("-")
                dtime = datetime(int(cal[0]), int(cal[1]), int(cal[2]))
                self.notice[2] = dtime
                self.get_date = False

################################################################################
# Stock Functions
################################################################################

def get_notice(id_num, lang = "en"):
    global http
    global url_side1
    global url_side2
    try:
        event_data = http.request("GET", url_side1 + str(id_num) + url_side2 + lang).data.decode("UTF-8")
        parser = EventPageParser(HTMLParser)
        parser.feed(event_data)
        parser.text = parser.trim()
        return parser
    except:
        print("Error while parsing notice!")
        error = exc_info()
        for e in error:
            print(e)
        return None
    return

def update_notices(lang = "en"):
    global http
    global notices
    try:
        notices = []
        r = http.request("GET", url_main + lang)
        asdf = r.data.decode("utf-8")
        parser = MainPageParser(HTMLParser, lang)
        parser.feed(asdf)
        notices.sort(key = lambda a: -a[1])
        # print(notices)
        return True
    except:
        print("Error in parsing main page!")
        error = exc_info()
        for e in error:
            print(e)
        return False

################################################################################
# Command Functions
################################################################################

async def get_notices(client=None, message=None, desc=False, usage=False):
    usage_text = "Usage: $notices [article_id]\nExample: $notices 1"
    if desc:
        return "Retrieves events from the Unison League notices. (Takes a few seconds...)"
    elif usage:
        return usage_text
    if client is None or message is None:
        return "Failed!"
    args = message.content.lower().split(" ")
    reply = ""
    global updated
    
    tosend = "" if message.server is None else message.author.mention + ", "
    tmp = await client.send_message(message.channel, tosend + "Fetching notices... this will take a bit. >.>")
    
    img = None
    
    if len(args) > 1:
        id_num = 0
        try:
            id_num = int(args[1])
        except:
            return usage_text
        notice = get_notice(id_num)
        if notice is None:
            tosend += "I wasn't able to find connect or find that notice... :<"
        else:
            reply = url_side1 + str(id_num) + url_side2 + "1&lang=en\n\n"
            reply += "**" + notice.title + "**" + notice.date + "\n\n"
            reply += notice.text
            if not notice.image is None:
                img = discord.Embed(color=discord.Color.purple())
                print(notice.image)
                try:
                    img.set_image(url=notice.image)
                except:
                    error = exc_info()
                    for a in error:
                        print(a)
            tosend += reply
    else:
        dtstart = datetime.now()
        if updated is None or dtstart.hour != updated.hour:
            success = update_notices()
            if not success:
                tosend += "I wasn't able to connect to the Unison League notices... :<"
            else:
                updated = dtstart
                # dtdelta = datetime.now() - dtstart
                reply = "**Notices:**"
                reply += "\nLast retrieved " + updated_string + "."
                for notice in notices:
                    reply += "\n - " + notice[0] + " (" + str(notice[1]) + ")"
                reply += "\nFor more information, use $notices <article_id>"
                tosend += reply
    await client.edit_message(tmp, tosend, embed=img)
    return

################################################################################
# Module Functions
################################################################################

commands = [[["notices", "news", "notice"], get_notices, True]]


def load(folder):
    return True


async def clock(client, time):
    return


async def reply(client, message):
    text = message.content.lower()
    for command in commands:
        for cmdname in command[0]:
            if text.startswith(cmdname):
                tosend = "" if message.server is None else "<@" + message.author.id + ">, "
                tmp = await client.send_message(message.channel, tosend + "Fetching notices... this will take a bit. >.>")
                tosend += command[1](message)
                await client.edit_message(tmp, tosend)
                return
                

