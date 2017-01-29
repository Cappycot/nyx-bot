# Bullshit spawn rates

import asyncio
from nyxspawner import get_emoji
from os import getcwd
from random import random, shuffle
from sys import exc_info

things = []

class SpawnItem:
    def __init__(self, name, url, prob, rarity):
        self.name = name;
        self.url = url;
        self.prob = prob;
        self.rank = rarity;
        global things
        for i in range(0, int(prob * 100)):
            things.append(self)
        

def load(folder):
    # R, formerly with prob rating of 1.0
    SpawnItem("Swelter Taurus","http://unisonleague.wikia.com/wiki/Swelter_Taurus_(Gear)", 1, 1)
    SpawnItem("Swelter Kong","http://unisonleague.wikia.com/wiki/Swelter_Kong_(Gear)", 1, 1)
    SpawnItem("Kin-ki","http://unisonleague.wikia.com/wiki/Kin-ki_(Gear)", 1, 1)
    SpawnItem("Croc Man","http://unisonleague.wikia.com/wiki/Croc_Man_(Gear)", 1, 1)
    SpawnItem("Mermaid","http://unisonleague.wikia.com/wiki/Mermaid_(Gear)", 1, 1)
    SpawnItem("Sea Serpent","http://unisonleague.wikia.com/wiki/Sea_Serpent_(Gear)", 1, 1)
    SpawnItem("Inky","http://unisonleague.wikia.com/wiki/Inky_(Gear)", 1, 1)
    SpawnItem("Kotaro the Stray Cat","http://unisonleague.wikia.com/wiki/Kotaro_the_Stray_Cat_(Gear)", 1, 1)
    SpawnItem("Crow Tengu","http://unisonleague.wikia.com/wiki/Crow_Tengu_(Gear)", 1, 1)
    SpawnItem("Kaava","http://unisonleague.wikia.com/wiki/Kaava_(Gear)", 1, 1)
    SpawnItem("Unicorn","http://unisonleague.wikia.com/wiki/Unicorn_(Gear)", 1, 1)
    SpawnItem("Exia Knight","http://unisonleague.wikia.com/wiki/Exia_Knight_(Gear)", 1, 1)
    SpawnItem("Val Leo","http://unisonleague.wikia.com/wiki/Val_Leo_(Gear)", 1, 1)
    SpawnItem("Banshee","http://unisonleague.wikia.com/wiki/Banshee_(Gear)", 1, 1)
    SpawnItem("Wyvern","http://unisonleague.wikia.com/wiki/Wyvern_(Gear)", 1, 1)
    SpawnItem("Medusa","http://unisonleague.wikia.com/wiki/Medusa_(Gear)", 1, 1)
    SpawnItem("Dullahan","http://unisonleague.wikia.com/wiki/Dullahan_(Gear)", 1, 1)
    SpawnItem("Cyclops","http://unisonleague.wikia.com/wiki/Cyclops_(Gear)", 1, 1)
    SpawnItem("Petrasaur","http://unisonleague.wikia.com/wiki/Petrasaur_(Gear)", 1, 1)
    SpawnItem("Golem","http://unisonleague.wikia.com/wiki/Golem_(Gear)", 1, 1)
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
    SpawnItem("Valkyrie Falarn","http://unisonleague.wikia.com/wiki/Valkyrie_Falarn_(Gear)", 0.10, 3)
    SpawnItem("Kagutsuchi","http://unisonleague.wikia.com/wiki/Kagutsuchi_(Gear)", 0.15, 3)
    SpawnItem("Abeno Seimei", "http://unisonleague.wikia.com/wiki/Abeno_Seimei_(Gear)", 0.15, 3)
    SpawnItem("Shinatobe, Beach Queen","http://unisonleague.wikia.com/wiki/Shinatobe,_Beach_Queen_(Gear)", 0.10, 3)
    SpawnItem("Joan of Arc","http://unisonleague.wikia.com/wiki/Joan_of_Arc_(Gear)", 0.15, 3)
    SpawnItem("Nobunaga","http://unisonleague.wikia.com/wiki/Nobunaga_(Gear)", 0.15, 3)
    SpawnItem("Apollo the Surfer","http://unisonleague.wikia.com/wiki/Apollo_the_Surfer_(Gear)", 0.1, 3)
    SpawnItem("Poseidon","http://unisonleague.wikia.com/wiki/Poseidon_(Gear)", 0.15, 3)
    SpawnItem("Valkyrie Raakyie","http://unisonleague.wikia.com/wiki/Valkyrie_Raakyie_(Gear)", 0.1, 3)
    SpawnItem("Siren","http://unisonleague.wikia.com/wiki/Siren_(Gear)", 0.15, 3)
    SpawnItem("Santa Flora","http://unisonleague.wikia.com/wiki/Santa_Flora_(Gear)", 0.1, 3)
    SpawnItem("Andromeda","http://unisonleague.wikia.com/wiki/Andromeda_(Gear)", 0.15, 3)
    SpawnItem("Ushiwakamaru","http://unisonleague.wikia.com/wiki/Ushiwakamaru_(Gear)", 0.15, 3)
    SpawnItem("Snow White","http://unisonleague.wikia.com/wiki/Snow_White_(Gear)", 0.1, 3)
    SpawnItem("Quetzalcoatl","http://unisonleague.wikia.com/wiki/Quetzalcoatl_(Gear)", 0.2, 3)
    SpawnItem("Shinatobe, Wind Caller","http://unisonleague.wikia.com/wiki/Shinatobe,_Wind_Caller_(Gear)", 0.15, 3)
    SpawnItem("Valkyrie Veere","http://unisonleague.wikia.com/wiki/Valkyrie_Veere_(Gear)", 0.1, 3)
    SpawnItem("Emilia, Dreamy Magic","http://unisonleague.wikia.com/wiki/Emilia,_Dreamy_Magic_(Gear)", 0.1, 3)
    SpawnItem("Gaia","http://unisonleague.wikia.com/wiki/Gaia_(Gear)", 0.1, 3)
    SpawnItem("Kirin","http://unisonleague.wikia.com/wiki/Kirin,_the_Wind_Beast_(Gear)", 0.15, 3)
    SpawnItem("Holiday Hel","http://unisonleague.wikia.com/wiki/Holiday_Hel_(Gear)", 0.1, 3)
    SpawnItem("Valkyrie","http://unisonleague.wikia.com/wiki/Valkyrie_(Gear)", 0.15, 3)
    SpawnItem("Indra, Storm God","http://unisonleague.wikia.com/wiki/Indra,_Storm_God_(Gear)", 0.15, 3)
    SpawnItem("Alice (French Maid)","http://unisonleague.wikia.com/wiki/Alice_(French_Maid)_(Gear)", 0.1, 3)
    SpawnItem("Nezha","http://unisonleague.wikia.com/wiki/Nezha_(Gear)", 0.15, 3)
    SpawnItem("Arthur, the Banneret","http://unisonleague.wikia.com/wiki/Arthur,_the_Banneret_(Gear)", 0.15, 3)
    SpawnItem("Athena","http://unisonleague.wikia.com/wiki/Athena_(Gear)", 0.1, 3)
    SpawnItem("Nyx the Songstress","http://unisonleague.wikia.com/wiki/Nyx_the_Songstress_(Gear)", 0.1, 3)
    SpawnItem("Lilith","http://unisonleague.wikia.com/wiki/Lilith_(Gear)", 0.2, 3)
    SpawnItem("Valkyrie Nikyt","http://unisonleague.wikia.com/wiki/Valkyrie_Nikyt_(Gear)", 0.1, 3)
    SpawnItem("Aizen","http://unisonleague.wikia.com/wiki/Aizen_(Gear)", 0.15, 3)
    SpawnItem("Anubis the Protector","http://unisonleague.wikia.com/wiki/Anubis_the_Protector_(Gear)", 0.15, 3)
    SpawnItem("Hel","http://unisonleague.wikia.com/wiki/Hel_(Gear)", 0.15, 3)
    SpawnItem("Merlyn","http://unisonleague.wikia.com/wiki/Merlyn_(Gear)", 0.1, 3)
    SpawnItem("HS Student Joan", "http://unisonleague.wikia.com/wiki/HS_Student_Joan_(Gear)", 0.1, 3)
    SpawnItem("Santa Lilith","http://unisonleague.wikia.com/wiki/Santa_Lilith_(Gear)", 0.1, 3)
    SpawnItem("Emilia, Tyro Witch","http://unisonleague.wikia.com/wiki/Emilia,_Tyro_Witch_(Gear)", 0.1, 3)
    SpawnItem("Skotos Athena", "http://unisonleague.wikia.com/wiki/Skotos_Athena_(Gear)", 0.1, 3)
    SpawnItem("Dragoon Cuchulainn","http://unisonleague.wikia.com/wiki/Dragoon_Cuchulainn_(Gear)", 0.1, 3)
    SpawnItem("Red Riding Hood","http://unisonleague.wikia.com/wiki/Red_Riding_Hood_(Gear)", 0.1, 3)
    SpawnItem("Melodic Fiine","http://unisonleague.wikia.com/wiki/Melodic_Fiine_(Gear)", 0.1, 3)
    SpawnItem("Sakuya, Sea Child","http://unisonleague.wikia.com/wiki/Sakuya,_Sea_Child_(Gear)", 0.1, 3)
    SpawnItem("Animus Athena", "http://unisonleague.wikia.com/wiki/Animus_Athena_(Gear)", 0.1, 3)
    SpawnItem("Oceanus Athena", "http://unisonleague.wikia.com/wiki/Oceanus_Athena_(Gear)", 0.1, 3);
    SpawnItem("Prox Athena", "http://unisonleague.wikia.com/wiki/Prox_Athena_(Gear)", 0.1, 3)
    SpawnItem("Mischievous Mary", "http://res.en.unisonleague.com/res_en/information/img/image/4455815.png", 0.1, 3)
    return True


async def clock(client, time):
    return

ranks = ["WTF", "R", "SR", "SSR"]

async def reply(client = None, message = None, **_):
    # "Spawning...\n:large_blue_circle: >>>>>>>> :red_circle: >>>>>>>> :yellow_heart: >>>>>>>> :rainbow:"
    tmp = await client.send_message(message.channel, "Spawning...\n:large_blue_circle: >>>>")
    spawnten = False
    svr = message.server
    try:
        arg = message.content.split(" ")[1].lower()
        spawnten = arg == "10" or arg == "ten"
    except:
        spawnten = False
    shuffle(things)
    toprank = 0
    spawned = None
    if spawnten:
        spawned = []
        for i in range(0, 10):
            aspawn = things[int(random() * len(things))]
            spawned.append(aspawn)
            toprank = max(toprank, aspawn.rank)
    else:
        spawned = things[int(random() * len(things))]
        toprank = spawned.rank
    await asyncio.sleep(1)
    if toprank == 1 and not spawnten:
        await client.edit_message(tmp, "Spawning...\n:large_blue_circle: >>>>>>>> " + get_emoji(1, svr) + "")
    else:
        await client.edit_message(tmp, "Spawning...\n:large_blue_circle: >>>>>>>> " + get_emoji(1, svr) + " >>>>")
        if spawnten and toprank == 1:
            for pity in things:
                if pity.rank == 2:
                    spawned[int(random() * 10)] = pity
                    toprank = 2
                    break;
        await asyncio.sleep(1)
        if (toprank == 2):
            await client.edit_message(tmp, "Spawning...\n:large_blue_circle: >>>>>>>> " + get_emoji(1, svr) + " >>>>>>>> " + get_emoji(2, svr) + "")
        else:
            await client.edit_message(tmp, "Spawning...\n:large_blue_circle: >>>>>>>> " + get_emoji(1, svr) + " >>>>>>>> " + get_emoji(2, svr) + " >>>>")
            await asyncio.sleep(1)
            await client.edit_message(tmp, "Spawning...\n:large_blue_circle: >>>>>>>> " + get_emoji(1, svr) + " >>>>>>>> " + get_emoji(2, svr) + " >>>>>>>> " + get_emoji(3, svr) + "")
    await asyncio.sleep(1)
    decor = "Spawning:\n"
    if spawnten:
        for spawn in spawned:
            decor += get_emoji(spawn.rank, svr) + " "
        await client.edit_message(tmp, decor)
        await asyncio.sleep(2)
    tosend = "" if message.server is None else "" + message.author.mention + ", "
    if spawnten:
        msg = "Congratulations! You spawned the following:"
        topurl = None
        for aspawn in spawned:
            msg += "\n" + aspawn.name + " (" + ranks[aspawn.rank] + ") at " + ("%.2f" % (aspawn.prob * 10000.0 / len(things))) + "% probability."
            if aspawn.rank == 3:
                msg += "\n" + aspawn.url
            elif toprank == aspawn.rank:
                topurl = aspawn.url
        if not topurl is None:
            msg += "\n" + topurl
    else:
        msg = "Congratulations! You spawned " + spawned.name + " (" + ranks[spawned.rank] + ") at " + ("%.2f" % (spawned.prob * 10000.0 / len(things))) + "% probability.\n" + spawned.url
    await client.edit_message(tmp, tosend + msg)
    return


commands = [[["spawnr", "spawno"], reply, False]]




