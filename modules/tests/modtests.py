###############################################################################
# Python Library Concept Tests
###############################################################################

import asyncio
import io
import os
from PIL import Image, ImageDraw, ImageFont
import urllib3
from sys import exc_info

http = urllib3.PoolManager()
testdir = None


###############################################################################
# Command Functions
###############################################################################

async def fear(client=None, message=None, **_):
    """Concept test of PIL usage and image editing..."""
    
    # Check to make sure everything is there.
    if client is None or message is None:
        return "Something disappeared... idk."
    elif len(message.mentions) > 1 or message.server is None:
        return "You have too many mentions..."
    
    # Get user to post
    tofear = message.mentions[0] if len(message.mentions) == 1 else message.author
    
    global testdir
    try:
        await client.send_typing(message.channel)
        url = tofear.avatar_url
        if not url:
            url = tofear.default_avatar_url
        
        # Presets for image creation
        avatarside = 240
        fpos = (522, 132)
        
        # Make http request for profile picture and get background
        tofear = Image.open(io.BytesIO(http.request("GET", url).data)).convert("RGBA")
        backdrop = Image.open(testdir + "/NoFearOneFear.png")
        
        # Paste avatar pic on top of backdrop as resized image
        tofear = tofear.resize((avatarside, avatarside), Image.LANCZOS)
        backdrop.paste(tofear, (fpos[0], fpos[1], fpos[0] + avatarside, fpos[1] + avatarside), mask=tofear)
        
        # Save in-memory filestream and send to Discord
        testpic = io.BytesIO()
        backdrop.save(testpic, format="png")
        # Move pointer to beginning so Discord can read pic.
        testpic.seek(0) 
        await client.send_file(message.channel, testpic, filename = "nofearonefear.png")
        return "We are all very afraid..."
    except:
        err = exc_info()
        for e in err:
            print(e)
        return "Uhh... something went wrong..."


async def flirt(client=None, message=None, **_):
    """Concept test of PIL ImageDraw text features..."""
    
    # Check to make sure everything is there.
    if client is None or message is None:
        return "Something wrong happened idk."
    
    text = None
    try:
        text = message.content.split(" ", 1)[1].strip()
        if len(text) > 100:
            return "Your text is too long!"
        elif "\n" in text:
            return "You can't have multiple lines!"
    except:
        return "What?"
    
    text = text.split(" ")
    flirtfont = ImageFont.truetype(testdir + "/animeace2_reg.ttf", 16)
    append = None
    width = 224     # height bound is about 108
    xstart = 18
    ycur = 360  # ystart
    ypad = 4

    try:
        await client.send_typing(message.channel)
        img = Image.open(testdir + "/flirtblank.png")
        draw = ImageDraw.Draw(img)

        for word in text:
            if append is None:
                append = word
            else:
                prev = append
                append += " " + word
                w, h = draw.textsize(append, font=flirtfont)
                if w > width:
                    append = word
                    draw.text((xstart, ycur), prev, fill=(0, 0, 0), font=flirtfont)
                    ycur += h + ypad
        draw.text((xstart, ycur), append, fill=(0, 0, 0), font=flirtfont)
        
        # Save in-memory filestream and send to Discord
        testpic = io.BytesIO()
        img.save(testpic, format="png")
        # Move pointer to beginning so Discord can read pic.
        testpic.seek(0) 
        await client.send_file(message.channel, testpic, filename = "flirt.png")
        return "*Flirt flirt...*"
    except:
        err = exc_info()
        for e in err:
            print(e)
        return "Uhh... something went wrong..."
    

async def obliterate(client=None, message=None, **_):
    """Concept test of PIL usage and image editing..."""
    
    # Check to make sure everything is there.
    if client is None or message is None:
        return "Our tank disappeared, sir!"
    elif len(message.mentions) != 1 or message.server is None:
        return "We couldn't get a target, sir!"
    elif message.mentions[0] == client.user:
        return "I'm your gunner... moron."
    elif message.author == message.mentions[0]:
        return "What? Do you have crippling depression?"
    
    # Get both users
    shooter = message.author
    victim = message.mentions[0]
    
    global testdir
    try:
        await client.send_typing(message.channel)
        # Get urls for profile pics
        url2 = victim.avatar_url
        if not url2:
            url2 = victim.default_avatar_url
        url1 = shooter.avatar_url
        if not url1:
            url1 = shooter.default_avatar_url
        
        # Presets for image creation
        avatarside = 80
        spos = (130, 42)
        vpos = (260, 360)
        
        # Make http request for profile pictures and get background tank
        shooter = Image.open(io.BytesIO(http.request("GET", url1).data)).convert("RGBA")
        victim = Image.open(io.BytesIO(http.request("GET", url2).data)).convert("RGBA")
        backdrop = Image.open(testdir + "/Obliterate.png")
        
        # Paste shooter on top of tank as resized image
        shooter = shooter.resize((avatarside, avatarside), Image.LANCZOS)
        backdrop.paste(shooter, (spos[0], spos[1], spos[0] + avatarside,
                                spos[1] + avatarside), mask=shooter)
                
        # backdrop.paste(shooter, (spos[0], spos[1],
        #                spos[0] + avatarside, spos[1] + avatarside))
        
        # Resize, tint, rotate, and paste victim
        victim = victim.resize((avatarside, avatarside), Image.LANCZOS)
        
        data = victim.getdata()
        new_data = []
        for i in range(0, len(data)):
            item = data[i]
            # Tint red and brighten a bit
            red = min(item[0] + 42, 255)
            green = min(item[1] + 9, 255)
            blue = max(item[2] - 9, 0)
            new_data.append((red, green, blue, item[3]))
        victim.putdata(new_data)
        
        victim = victim.rotate(-40, expand = True)
        vw = victim.size[0]
        vh = victim.size[1]
        backdrop.paste(victim, (vpos[0], vpos[1], vpos[0] + vw,
                                vpos[1] + vh), mask=victim)
        
        # Save in-memory filestream and send to Discord
        testpic = io.BytesIO()
        backdrop.save(testpic, format="png")
        # Move pointer to beginning so Discord can read pic.
        testpic.seek(0)
        await client.send_file(message.channel, testpic, filename = "bwaarp.png")
        return "Another one bites the dust! ``*CLAP*``"
    except:
        err = exc_info()
        for e in err:
            print(e)
        return "Uhh... we misfired, sir!"


commands = [[["fear"], fear, "When you or someone else is scary.", "fear [@user]", 1],
            [["flirt"], flirt, "Generates the pickup line as fire in comic.", "flirt <text>", 1],
            [["obliterate", "destroy", "pwn"], obliterate, "Reks a user.", "obliterate @user", 1]]


def init(module = None, **_):
    if module is None:
        return False
    global testdir
    testdir = module.folder
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    module.make_primary()
    return True




