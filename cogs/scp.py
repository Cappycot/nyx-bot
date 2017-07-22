"""
Secure, Contain, Protect

This module requires Beautiful Soup 4.X.X to run!
"""

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import BucketType
from os import mkdir
from os.path import isdir, join
from re import compile, search

# Name of the directory to be used to store things...
folder = "scp"
titles_file = "titles.txt"
# SCP series 4 is the most current...
highest_scp = 3999
series_range = (highest_scp + 1) // 1000
# SCPs range from 001 to 3999...
titles = {(i + 1): None for i in range(highest_scp)}


def read_component(thing):
    if isinstance(thing, Tag):
        if thing.name == "em":
            return "*" + read_component(thing.next_element) + "*"
        elif thing.name == "strong":
            return "**" + read_component(thing.next_element) + "**"
        elif thing.name == "u":
            return "__" + read_component(thing.next_element) + "__"
        elif thing.attrs.get("style") == "text-decoration: line-through;":
            return "~~" + read_component(thing.next_element) + "~~"
        else:
            return read_component(thing.next_element)
    else:
        return thing


def fetch_level(element, limit=1024):
    length = 0
    parts = []
    if element is None:
        return "[DATA ERROR]"
    # component = read_component(element)
    # if component:
    # length = len(component)
    # If one paragraph is more than 1024 characters maybe the SCP isn't
    # worth reading lol
    # if length > limit:
    # return "[WITHHELD]"
    # parts.append(component)
    for thing in [element] + list(element.next_siblings):
        # component = read_component(thing)
        if isinstance(thing, Tag):
            if thing.name == "em":
                component = "*" + fetch_level(thing.next_element) + "*"
            elif thing.name == "strong":
                component = "**" + fetch_level(thing.next_element) + "**"
            elif thing.name == "u":
                component = "__" + fetch_level(thing.next_element) + "__"
            elif thing.attrs.get("style") == "text-decoration: line-through;":
                component = "~~" + fetch_level(thing.next_element) + "~~"
            else:
                component = fetch_level(thing.next_element)
        else:
            component = thing
        if component:
            length += len(component)
            if length > limit - 3:
                if not component.endswith(".") or length > limit:
                    break
            else:
                parts.append(component)
    if len(parts) == 0:
        return "[WITHHELD]"
    return "".join(parts).strip("-:, ")


def save_titles():
    try:
        if not isdir(folder):
            mkdir(folder)
        data = open(join(folder, titles_file), "w")
        for num in titles:
            if titles[num] is not None:
                data.write("".join([str(num), "=", titles[num], "\n"]))
            else:
                print(str(num))
        data.flush()
        data.close()
        return True
    except FileExistsError:
        return False


async def get_titles(loop):
    async with ClientSession(loop=loop) as session:
        for series in range(series_range):
            url = "http://scp-wiki.wikidot.com/scp-series"
            if series > 0:
                url += "-" + str(series + 1)
            print(url)
            async with session.get(url) as req:
                if req.status == 200:
                    soup = BeautifulSoup(await req.read(), "html.parser")
                    for num in range(1000):
                        num += series * 1000
                        if num < 10:
                            number = "00" + str(num)
                        elif num < 100:
                            number = "0" + str(num)
                        else:
                            number = str(num)
                        element = soup.find("a", string="SCP-" + number)
                        if element is not None:
                            titles[num] = fetch_level(element.next_sibling)
                else:
                    return False
    return save_titles()


async def load_titles(loop, force_fetch=False):
    if not force_fetch:
        try:
            data = open(join(folder, titles_file), "r")
            for line in data:
                args = line.split("=", 1)
                titles[int(args[0])] = args[1]
        except FileNotFoundError or IndexError or ValueError:
            force_fetch = True
    if force_fetch:
        return await get_titles(loop)
    return True


async def parse_scp(ctx, number: str, post_image=False):
    url = "http://scp-wiki.wikidot.com/scp-" + number
    message = await ctx.send("Fetching SCP information...")
    async with ctx.message.channel.typing(), ClientSession(
            loop=ctx.bot.loop) as session, session.get(url) as req:
        if req.status == 200:
            # TODO: Figure out how to break up time-consuming thread...
            embed = Embed(title="SCP-" + number,
                          description=titles[int(number)],
                          url=url)
            source = BeautifulSoup(await req.read(), "html.parser")

            # Get the SCP class...
            object_class = source.find(
                string=compile("Object Class[:]?$")) or source.find(
                string=compile("Classification[:]?$"))
            # If you're the person who uses "Classification" f*ck off pls...
            if object_class is None:
                object_class = "[WITHHELD]"
            elif not object_class.next_element.strip():
                classes = []
                for sibling in object_class.next_element.next_siblings:
                    if sibling is not None:
                        if isinstance(sibling, Tag) and \
                                        sibling.next_element is not None:
                            element = sibling.next_element.strip(": ")
                            classes.append("~~" + element + "~~")
                        elif sibling.strip():
                            classes.append(sibling.strip())
                object_class = " ".join(classes)
            else:
                object_class = object_class.next_element.strip(": ")
            embed.add_field(name="Object Class:", value=object_class)

            # Color the embed based on class...
            object_class = object_class.lower()
            if search("safe$", object_class):
                embed.colour = Color.green()
            elif search("euclid$", object_class):
                embed.colour = Color.gold()
            elif search("keter$", object_class):
                embed.colour = Color.red()
            elif search("thaumiel$", object_class):
                embed.colour = Color.blue()
            elif search("apollyon$", object_class):
                embed.colour = Color.red()

            # Fetch the containment procedures and description...
            containment = source.find(
                string=compile("Special Containment Procedure[s]?[:]?$"))
            if containment is None or containment.next_element is None:
                containment = "[DATA ERROR]"
            else:
                containment = fetch_level(containment.next_element)
                if search("[.][~*_'\"]*$", containment) is None:
                    containment += "..."
            embed.add_field(name="Special Containment Procedures:",
                            value=containment)
            description = source.find(string=compile("Description[:]?$"))
            if description is None or description.next_element is None:
                description = "[DATA ERROR]"
            else:
                description = fetch_level(description.next_element)
                if search("[.][~*_'\"]*$", description) is None:
                    description += "..."
            embed.add_field(name="Description:", value=description)

            # Locate the image...
            image = source.find("div", compile("scp-image-block"))
            if post_image and image is not None:
                image = image.next_element
                if image is not None and isinstance(image, Tag):
                    image = image.get("src")
                    if image is not None:
                        embed.set_image(url=image)
            await ctx.send(embed=embed)
        elif req.status == 404:
            await ctx.send(
                "Such an SCP is either classified or does not exist...")
        else:
            await ctx.send("An error occurred. ({})".format(str(req.status)))
    await message.delete()


class SCP:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def scp(self, ctx, number: int):
        """Retrieves information on a particular SCP."""
        if number <= 0:
            return
        elif number < 10:
            number = "00" + str(number)
        elif number < 100:
            number = "0" + str(number)
        else:
            number = str(number)
        await parse_scp(ctx, number, post_image=True)


def setup(bot):
    bot.loop.run_until_complete(load_titles(bot.loop))
    bot.add_cog(SCP(bot))
