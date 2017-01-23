################################################################################
# The Great Emoji Race
################################################################################

import asyncio
import discord
from discord.utils import find
from random import randint, shuffle

join_time = 30 # in seconds
max_players = 8 # 2 <= max <= 8
max_speed = 16
max_change = int(max_speed / 2)
min_speed = 4
push_threshold = 10
races = {}
display = ["one", "two", "three", "four", "five", "six", "seven", "eight"]
place = [":trophy:", "``2nd``", "``3rd``", "``4th``", "``5th``", "``6th``", "``7th``", ":joy:"]


class Race:
    def __init__(self, channel):
        self.channel = channel
        self.finished = 1
        self.push = 0 # Number of messages that are pushing the race up.
        self.racers = []
        self.scrambled = None
        self.racing = False
    
    def get_winner(self):
        if not self.is_finished():
            return None
        for racer in self.racers:
            if racer.place == 1:
                return racer
    
    def is_finished(self):
        return all(a.place for a in self.racers)
    
    def render(self):
        toreturn = ":checkered_flag:``|------------------------------------------------|``:checkered_flag:\n"
        for i in range(0, len(self.racers)):
            racer = self.racers[i]
            toreturn += ":" + display[i] + ":"
            if int(racer.progress / 2) > 0:
                toreturn += "``" + ">" * int(racer.progress / 2) + "``"
            toreturn += racer.emoji
            if racer.place:
                toreturn += place[racer.place - 1]
            toreturn += "\n"
        toreturn += ":checkered_flag:``|------------------------------------------------|``:checkered_flag:"
        return toreturn
    
    def step(self):
        if self.is_finished():
            return
        if self.scrambled is None:
            self.scrambled = self.racers[:]
        shuffle(self.scrambled)
        for racer in self.scrambled:
            if racer.place:
                continue
            racer.progress += racer.speed
            if racer.progress >= 100:
                racer.progress = 100
                racer.place = self.finished
                self.finished += 1
            else:
                racer.speed += randint(-max_change, max_change)
                if racer.speed < min_speed:
                    racer.speed = min_speed
                elif racer.speed > max_speed:
                    racer.speed = max_speed


class Racer:
    def __init__(self, member, emoji):
        self.emoji = emoji
        self.member = member
        self.place = None
        self.progress = 0
        self.speed = randint(min_speed, randint(int(max_speed / 2), max_speed))


################################################################################
# Race Function
################################################################################

async def joinrace(message = None, **_):
    if message.server is None:
        return "Racing doesn't work here!"
    elif not message.server.id in races:
        return "there is no race to join!"
    race = races[message.server.id]
    if race.racing:
        return "the race is already underway!"
    elif find(lambda a: a.member == message.author, race.racers):
        return "you already joined this race!"
    elif len(race.racers) >= max_players:
        return "the current race is full!"
    try:
        emoji = message.content.split(" ")[1]
        if len(emoji) != 1:
            if emoji.startswith("<"):
                test = emoji.split(":")[2][:-1]
                if find(lambda a: a.id == test, message.server.emojis) is None:
                    return "invalid emoji!"
            else:
                return "invalid emoji!"
        for existing in race.racers:
            if existing.emoji == emoji:
                return "that emoji is already taken!"
        racer = Racer(message.author, emoji)
        race.racers.append(racer)
        return "you've joined the race as " + emoji + "!"
    except:
        return "invalid emoji!"


async def race(client = None, message = None, **_):
    if message.server is None:
        return "Racing doesn't work here!"
    if message.server.id in races:
        race = races[message.server.id]
        return "there is already a race in progress!"
    race = Race(message.channel)
    races[message.server.id] = race
    await client.send_message(message.channel, "Race starting in " + str(join_time) + " seconds! Use $join <emoji> to join!")
    time = 0
    while time < join_time and len(race.racers) < max_players:
        await asyncio.sleep(1)
        time += 1
    race.racing = True
    if len(race.racers) < 2:
        await client.send_message(message.channel, "Race aborted. Not enough racers...")
    else:
        racetrack = await client.send_message(message.channel, "Let the Great Emoji Race begin!\n" + race.render())
        await asyncio.sleep(2)
        while not race.is_finished():
            await asyncio.sleep(2)
            race.step()
            await client.edit_message(racetrack, "Let the Great Emoji Race begin!\n" + race.render())
        await asyncio.sleep(2)
        winner = race.get_winner()
        et = discord.Embed(title = "The Great Emoji Race", description = winner.member.mention + " as " + winner.emoji + " has won the race!", color = discord.Color.green())
        await client.edit_message(racetrack, "The Great Emoji Race has concluded!\n" + race.render(), embed = et)
    del races[message.server.id]
    

commands = [[["start"], race, "Starts a new race if there is none on the server.", "start", 1],
            [["join"], joinrace, "Joins the server race with an emoji if there is one about to start.", "join <emoji>", 1]]


################################################################################
# Module Functions
################################################################################

def init(module = None, loadstring = None, **_):
    if module is None:
        return False
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    return True




