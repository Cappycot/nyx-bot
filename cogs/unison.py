from configparser import ConfigParser
from os.path import join

from discord.ext import commands


class Event:
    def __init__(self, name, daily, disabled, utc):
        self.name = name
        self.daily = False
        self.disabled = False
        self.times = []
        self.utc = utc

    def find(self, time, utc_time):
        pass

    def find_next(self, time, utc_time):
        pass


folder = "unison"
events_folder = "events"
aliases_file = "Aliases.dat"
events_file = "Events.dat"
remind_folder = "reminders"
events = {}


def load_events():
    global events
    config = ConfigParser()
    events = {}
    config.read(join(folder, events_folder, events_file))
    for section in config.sections():
        name = section
        section = config[name]
        event = Event(name, section.getboolean("daily"),
                      section.getboolean("disabled"),
                      section.getboolean("utc"))
        data = open(join(folder, events_folder, section["file"]))
        for line in data:
            line = line.strip("\n ")
            if not line or line.startswith("#"):
                continue
            times = line.split("-")
            event.times.append([int(times[0]), int(times[1])])
        event.times.sort(key=lambda a: a[0])
        events[section["id"]] = event


class Unison:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.group(aliases=["event"])
    async def events(self, ctx):
        print("Events")

    @events.command()
    async def list(self, ctx, *args):
        print("List")

    @events.command()
    async def next(self, ctx, *args):
        print("Next")

    @events.command()
    async def remind(self, ctx, *args):
        print("Remind")


def setup(nyx):
    load_events()
    unison = Unison(nyx)
    nyx.add_cog(unison)
