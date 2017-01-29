# Terrible (standard) spawn rates

import asyncio
from os import getcwd
from random import randint, shuffle
from sys import exc_info


ranks = ["WTF", "R", "SR", "SSR"]
emoji = [":large_blue_circle:", ":red_circle:", ":yellow_heart:", ":rainbow:"]
semoji = [":large_blue_circle:", "<:rare:230893693371023360>", "<:srare:230893706004267010>", "<:ssrare:230893713428185088>"]
spawns = []
things = []
things.append([])
things.append([])
things.append([])
things.append([])

def get_emoji(index, server):
    if not server is None:
        if server.id == "137093566160830465":
            return semoji[index]
    return emoji[index]


class SpawnItem:
    def __init__(self, name, url, prob, rarity, generic = False):
        self.name = name
        self.url = url
        self.prob = prob
        self.rank = rarity
        self.generic = generic
        if generic:
            global spawns
            for i in range(0, int(prob * 100)):
                spawns.append(self)
        else:
            global things
            things[rarity].append(self)
    def __str__(self):
        global ranks
        return ranks[self.rank]

rch = 0.80
srch = 0.18
ssrch = 0.02

def calc_prob(spawn):
    rank = spawn.rank
    prob = rch
    if rank == 2:
        prob = srch
    elif rank == 3:
        prob = ssrch
    prob /= len(things[rank])
    return " at " + ("%.2f" % (prob * 100)) + "% probability."


def load(folder):
    # R, SR, SSR selection
    global rch
    global srch
    global ssrch
    SpawnItem(None, None, rch, 1, True)
    SpawnItem(None, None, srch, 2, True)
    SpawnItem(None, None, ssrch, 3, True)
    # R, formerly with prob rating of 1.0
    SpawnItem("Swelter Taurus","http://unisonleague.wikia.com/wiki/Swelter_Taurus_(Gear)", 1.5, 1)
    SpawnItem("Swelter Kong","http://unisonleague.wikia.com/wiki/Swelter_Kong_(Gear)", 1.5, 1)
    SpawnItem("Kin-ki","http://unisonleague.wikia.com/wiki/Kin-ki_(Gear)", 1.5, 1)
    SpawnItem("Croc Man","http://unisonleague.wikia.com/wiki/Croc_Man_(Gear)", 1.5, 1)
    SpawnItem("Mermaid","http://unisonleague.wikia.com/wiki/Mermaid_(Gear)", 1.5, 1)
    SpawnItem("Sea Serpent","http://unisonleague.wikia.com/wiki/Sea_Serpent_(Gear)", 1.5, 1)
    SpawnItem("Inky","http://unisonleague.wikia.com/wiki/Inky_(Gear)", 1.5, 1)
    SpawnItem("Kotaro the Stray Cat","http://unisonleague.wikia.com/wiki/Kotaro_the_Stray_Cat_(Gear)", 1.5, 1)
    SpawnItem("Crow Tengu","http://unisonleague.wikia.com/wiki/Crow_Tengu_(Gear)", 1.5, 1)
    SpawnItem("Kaava","http://unisonleague.wikia.com/wiki/Kaava_(Gear)", 1.5, 1)
    SpawnItem("Unicorn","http://unisonleague.wikia.com/wiki/Unicorn_(Gear)", 1.5, 1)
    SpawnItem("Exia Knight","http://unisonleague.wikia.com/wiki/Exia_Knight_(Gear)", 1.5, 1)
    SpawnItem("Val Leo","http://unisonleague.wikia.com/wiki/Val_Leo_(Gear)", 1.5, 1)
    SpawnItem("Banshee","http://unisonleague.wikia.com/wiki/Banshee_(Gear)", 1.5, 1)
    SpawnItem("Wyvern","http://unisonleague.wikia.com/wiki/Wyvern_(Gear)", 1.5, 1)
    SpawnItem("Medusa","http://unisonleague.wikia.com/wiki/Medusa_(Gear)", 1.5, 1)
    SpawnItem("Dullahan","http://unisonleague.wikia.com/wiki/Dullahan_(Gear)", 1.5, 1)
    SpawnItem("Cyclops","http://unisonleague.wikia.com/wiki/Cyclops_(Gear)", 1.5, 1)
    SpawnItem("Petrasaur","http://unisonleague.wikia.com/wiki/Petrasaur_(Gear)", 1.5, 1)
    SpawnItem("Golem","http://unisonleague.wikia.com/wiki/Golem_(Gear)", 1.5, 1)
    # SR 
    SpawnItem("Firedrake Ignis","http://unisonleague.wikia.com/wiki/Firedrake_Ignis_(Gear)", 0.5, 2)
    SpawnItem("Ninetail Fox","http://unisonleague.wikia.com/wiki/Ninetail_Fox_(Gear)", 0.5, 2)
    SpawnItem("Leviathan","http://unisonleague.wikia.com/wiki/Leviathan_(Gear)", 0.5, 2)
    SpawnItem("Fenrir","http://unisonleague.wikia.com/wiki/Fenrir_(Gear)", 0.5, 2)
    SpawnItem("Hraesvelgr","http://unisonleague.wikia.com/wiki/Hraesvelgr_(Gear)", 0.5, 2)
    SpawnItem("Cuchulainn","http://unisonleague.wikia.com/wiki/Cuchulainn_(Gear)", 0.5, 2)
    SpawnItem("Etherful Golem","http://unisonleague.wikia.com/wiki/Etherful_Golem_(Gear)", 0.5, 2)
    SpawnItem("Physoth, Sacred Beast","http://unisonleague.wikia.com/wiki/Physoth,_Sacred_Beast_(Gear)", 0.5, 2)
    SpawnItem("Diablos","http://unisonleague.wikia.com/wiki/Diablos_(Gear)", 0.5, 2)
    SpawnItem("Metus, Evil Drake","http://unisonleague.wikia.com/wiki/Metus,_Evil_Drake_(Gear)", 0.5, 2)
    # SSR 
    SpawnItem("Behemoth","http://unisonleague.wikia.com/wiki/Behemoth_(Gear)", 0.20, 3)
    SpawnItem("Kagutsuchi","http://unisonleague.wikia.com/wiki/Kagutsuchi_(Gear)", 0.15, 3)
    SpawnItem("Joan of Arc","http://unisonleague.wikia.com/wiki/Joan_of_Arc_(Gear)", 0.15, 3)
    SpawnItem("Nobunaga","http://unisonleague.wikia.com/wiki/Nobunaga_(Gear)", 0.15, 3)
    SpawnItem("Poseidon","http://unisonleague.wikia.com/wiki/Poseidon_(Gear)", 0.15, 3)
    SpawnItem("Siren","http://unisonleague.wikia.com/wiki/Siren_(Gear)", 0.15, 3)
    SpawnItem("Andromeda","http://unisonleague.wikia.com/wiki/Andromeda_(Gear)", 0.15, 3)
    SpawnItem("Ushiwakamaru","http://unisonleague.wikia.com/wiki/Ushiwakamaru_(Gear)", 0.15, 3)
    SpawnItem("Snow White","http://unisonleague.wikia.com/wiki/Snow_White_(Gear)", 0.1, 3)
    SpawnItem("Quetzalcoatl","http://unisonleague.wikia.com/wiki/Quetzalcoatl_(Gear)", 0.2, 3)
    SpawnItem("Shinatobe, Wind Caller","http://unisonleague.wikia.com/wiki/Shinatobe,_Wind_Caller_(Gear)", 0.15, 3)
    SpawnItem("Kirin","http://unisonleague.wikia.com/wiki/Kirin,_the_Wind_Beast_(Gear)", 0.15, 3)
    SpawnItem("Indra, Storm God","http://unisonleague.wikia.com/wiki/Indra,_Storm_God_(Gear)", 0.15, 3)
    SpawnItem("Nezha","http://unisonleague.wikia.com/wiki/Nezha_(Gear)", 0.15, 3)
    SpawnItem("Lilith","http://unisonleague.wikia.com/wiki/Lilith_(Gear)", 0.2, 3)
    SpawnItem("Aizen","http://unisonleague.wikia.com/wiki/Aizen_(Gear)", 0.15, 3)
    SpawnItem("Anubis the Protector","http://unisonleague.wikia.com/wiki/Anubis_the_Protector_(Gear)", 0.15, 3)
    SpawnItem("Hel","http://unisonleague.wikia.com/wiki/Hel_(Gear)", 0.15, 3)
    SpawnItem("Merlyn","http://unisonleague.wikia.com/wiki/Merlyn_(Gear)", 0.1, 3)
    SpawnItem("Red Riding Hood","http://unisonleague.wikia.com/wiki/Red_Riding_Hood_(Gear)", 0.1, 3)
    SpawnItem("Melodic Fiine","http://unisonleague.wikia.com/wiki/Melodic_Fiine_(Gear)", 0.1, 3)
    return True


def get_spawns(ten, masesq):
    spawned = []
    toprank = 3
    shuffle(spawns)
    if masesq:
        for i in range(0, 10):
            ssrs = len(things[3]) - 1
            spawned.append(things[3][randint(0, ssrs)])
    else:
        toprank = 0
        chances = len(spawns) - 1
        for i in range(0, ten and 10 or 1):
            thisrank = spawns[randint(0, chances)].rank
            mons = len(things[thisrank]) - 1
            spawn = things[thisrank][randint(0, mons)]
            toprank = toprank > spawn.rank and toprank or spawn.rank
            spawned.append(spawn)
        if ten and toprank < 2:
            srs = len(things[2]) - 1
            spawned[randint(0, 9)] = things[2][randint(0, srs)]
            toprank = 2
    return {"spawned": spawned, "toprank": toprank}
    
    
    
async def reply(client = None, message = None, **_):
    # "Spawning...\n:large_blue_circle: >>>>>>>> :red_circle: >>>>>>>> :yellow_heart: >>>>>>>> :rainbow:"
    
    svr = message.server
    decor = "Spawning...\n" + get_emoji(0, svr) + " >>>>"
    tmp = await client.send_message(message.channel, decor)
    masesq = message.content.startswith("spawnmasesq")
    spawnten = False
    try:
        spl = message.content.split(" ")
        arg = spl[1].lower()
        key = spl[0]
        spawnten = arg == "10" or arg == "ten"
        masesq = key == "spawnmasesq" or arg == "masesq"
    except:
        spawnten = False
    
    result = get_spawns(spawnten, masesq)
    toprank = result["toprank"]
    spawned = result["spawned"]
    
    await asyncio.sleep(1)
    if toprank > 1:
        decor += ">>>> " + get_emoji(1, svr) + " >>>>"
        await client.edit_message(tmp, decor)
        await asyncio.sleep(1)
        if toprank > 2:
            decor += ">>>> " + get_emoji(2, svr) + " >>>>"
            await client.edit_message(tmp, decor)
            await asyncio.sleep(1)
    decor += ">>>>"
    for spawn in spawned:
        decor += " " + get_emoji(spawn.rank, svr) + " "
    
    await client.edit_message(tmp, decor)
        
    await asyncio.sleep(2)
        
    tosend = "" if message.server is None else "<@" + message.author.id + ">, "
    if spawnten or masesq:
        msg = "Congratulations! You spawned the following:"
        topurl = None
        for aspawn in spawned:
            msg += "\n" + aspawn.name + " (" + ranks[aspawn.rank] + ")" + calc_prob(aspawn)
            if aspawn.rank == 3 and not masesq:
                msg += "\n" + aspawn.url
            elif toprank == aspawn.rank:
                topurl = aspawn.url
        if not topurl is None:
            msg += "\n" + topurl
    else:
        msg = "Congratulations! You spawned " + spawned[0].name + " (" + ranks[spawned[0].rank] + ")" + calc_prob(spawned[0]) + "\n" + spawned[0].url
    await client.edit_message(tmp, tosend + msg)
    return

commands = [[["spawnm"], reply, False]]


async def clock(client, time):
    return




