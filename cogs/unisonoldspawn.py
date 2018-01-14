# Bullshit spawn rates

import asyncio
from random import randint

from discord.ext import commands
from discord.ext.commands import BucketType

from nyx.nyxutils import reply

ranks = ["WTF", "R", "SR", "SSR"]
emoji = [":large_blue_circle:", "<:rare:230893693371023360>",
         "<:srare:230893706004267010>", "<:ssrare:230893713428185088>"]
pity = []
things = []
url_prefix = "http://unisonleague.wikia.com/wiki/"


class SpawnItem:
    def __init__(self, name, url, prob, rarity):
        self.name = name
        self.url = url
        self.prob = prob
        self.rank = rarity
        global pity
        global things
        if rarity == 2:
            pity.append(self)
        for i in range(0, int(prob * 100)):
            things.append(self)


def load():
    # R, formerly with prob rating of 1.0
    SpawnItem("Swelter Taurus", "Swelter_Taurus_(Gear)", 2, 1)
    SpawnItem("Swelter Kong", "Swelter_Kong_(Gear)", 2, 1)
    SpawnItem("Kin-ki", "Kin-ki_(Gear)", 2, 1)
    SpawnItem("Croc Man", "Croc_Man_(Gear)", 2, 1)
    SpawnItem("Mermaid", "Mermaid_(Gear)", 2, 1)
    SpawnItem("Sea Serpent", "Sea_Serpent_(Gear)", 2, 1)
    SpawnItem("Inky", "Inky_(Gear)", 2, 1)
    SpawnItem("Kotaro the Stray Cat", "Kotaro_the_Stray_Cat_(Gear)", 2, 1)
    SpawnItem("Crow Tengu", "Crow_Tengu_(Gear)", 2, 1)
    SpawnItem("Kaava", "Kaava_(Gear)", 2, 1)
    SpawnItem("Unicorn", "Unicorn_(Gear)", 2, 1)
    SpawnItem("Exia Knight", "Exia_Knight_(Gear)", 2, 1)
    SpawnItem("Val Leo", "Val_Leo_(Gear)", 2, 1)
    SpawnItem("Banshee", "Banshee_(Gear)", 2, 1)
    SpawnItem("Wyvern", "Wyvern_(Gear)", 2, 1)
    SpawnItem("Medusa", "Medusa_(Gear)", 2, 1)
    SpawnItem("Dullahan", "Dullahan_(Gear)", 2, 1)
    SpawnItem("Cyclops", "Cyclops_(Gear)", 2, 1)
    SpawnItem("Petrasaur", "Petrasaur_(Gear)", 2, 1)
    SpawnItem("Golem", "Golem_(Gear)", 2, 1)
    # SR
    SpawnItem("Firedrake Ignis", "Firedrake_Ignis_(Gear)", 1, 2)
    SpawnItem("Ninetail Fox", "Ninetail_Fox_(Gear)", 1, 2)
    SpawnItem("Leviathan", "Leviathan_(Gear)", 1, 2)
    SpawnItem("Fenrir", "Fenrir_(Gear)", 1, 2)
    SpawnItem("Hraesvelgr", "Hraesvelgr_(Gear)", 1, 2)
    SpawnItem("Cuchulainn", "Cuchulainn_(Gear)", 1, 2)
    SpawnItem("Etherful Golem", "Etherful_Golem_(Gear)", 1, 2)
    SpawnItem("Physoth, Sacred Beast", "Physoth,_Sacred_Beast_(Gear)", 1, 2)
    SpawnItem("Diablos", "Diablos_(Gear)", 1, 2)
    SpawnItem("Metus, Evil Drake", "Metus,_Evil_Drake_(Gear)", 1, 2)
    # SSR: http://unisonleague.wikia.com/wiki/Monster_Encyclopedia/SSR
    # Give crappier SSR mons 0.2 chance.
    # Give standard SSR mons 0.15 chance.
    # Give better and reforgeable collab SSR mons 0.1 chance.
    # Give best SSR mons 0.05 chance.
    # Give cosplay and non-reforgeable collab SSR mons 0.01 chance.

    # Fire SSRs
    SpawnItem("Behemoth", "Behemoth_(Gear)", 0.2, 3)
    SpawnItem("Valkyrie Falarn", "Valkyrie_Falarn_(Gear)", 0.1, 3)
    SpawnItem("Kagutsuchi", "Kagutsuchi_(Gear)", 0.15, 3)
    SpawnItem("Abeno Seimei", "Abeno_Seimei_(Gear)", 0.15, 3)
    SpawnItem("Shinatobe, Beach Queen", "Shinatobe,_Beach_Queen_(Gear)", 0.01,
              3)
    SpawnItem("Joan of Arc", "Joan_of_Arc_(Gear)", 0.15, 3)
    SpawnItem("Prox Athena", "Prox_Athena_(Gear)", 0.1, 3)
    SpawnItem("Nobunaga", "Nobunaga_(Gear)", 0.15, 3)
    SpawnItem("Apollo the Surfer", "Apollo_the_Surfer_(Gear)", 0.1,
              3)  # May change to 0.05
    SpawnItem("Abeno Seimei", "Abeno_Seimei_(Gear)", 0.1, 3)
    SpawnItem("Ares", "Ares_(Gear)", 0.05, 3)
    SpawnItem("Verdandi", "Verdandi_(Gear)", 0.05, 3)
    SpawnItem("Salamander", "Salamander_(Gear)", 0.05, 3)
    SpawnItem("Kyoko Sakura", "Kyoko_Sakura_(Gear)", 0.01, 3)
    SpawnItem("Nezha, Celestial Boy", "Nezha,_Celestial_Boy_(Gear)", 0.1, 3)
    SpawnItem("Eva-02", "Eva-02_(Gear)", 0.01, 3)
    SpawnItem("Asuka Shikinami Langley", "Asuka_Shikinami_Langley_(Gear)",
              0.01, 3)
    SpawnItem("Eva-02 RT (F Type)", "Eva-02_RT_(F_Type)_(Gear)", 0.01, 3)
    SpawnItem("Kagamine Rin", "Kagamine_Rin_(Gear)", 0.01, 3)
    SpawnItem("Berserker", "Berserker_(Gear)", 0.01, 3)
    SpawnItem("Archer", "Archer_(Gear)", 0.01, 3)
    SpawnItem("Misato Katsuragi", "_(Gear)", 0.01, 3)
    SpawnItem("~~BDSM~~ Elizabeth", "Elizabeth_(Gear)", 0.05, 3)
    SpawnItem("Yukata Miku", "Yukata_Miku_(Gear)", 0.01, 3)

    # Water SSRs
    # SpawnItem("", "_(Gear)", 0.01, 3)
    SpawnItem("Poseidon", "Poseidon_(Gear)", 0.2, 3)
    SpawnItem("Wind Empress, Dies", "Wind_Empress,_Dies_(Gear)", 0.01, 3)
    SpawnItem("~~Dat Ass~~ Valkyrie Raakyie", "Valkyrie_Raakyie_(Gear)", 0.1,
              3)
    SpawnItem("Siren", "Siren_(Gear)", 0.15, 3)
    SpawnItem("Santa Flora", "Santa_Flora_(Gear)", 0.1, 3)
    SpawnItem("Andromeda", "Andromeda_(Gear)", 0.15, 3)
    SpawnItem("Ushiwakamaru", "Ushiwakamaru_(Gear)", 0.15, 3)
    SpawnItem("Snow White", "Snow_White_(Gear)", 0.1, 3)
    SpawnItem("Yule Kirin", "Yule_Kirin_(Gear)", 0.1, 3)  # May change to 0.05
    SpawnItem("Urd", "Urd_(Gear)", 0.05, 3)
    SpawnItem("Mercury", "Mercury_(Gear)", 0.05, 3)
    SpawnItem("Tsuyukusa", "Tsuyukusa_(Gear)", 0.05, 3)
    SpawnItem("Sayaka Miki", "Sayaka_Miki_(Gear)", 0.01, 3)
    SpawnItem("Oceanus Athena", "Oceanus_Athena_(Gear)", 0.1, 3)
    SpawnItem("Eva-00", "Eva-00_(Gear)", 0.01, 3)
    SpawnItem("Rei Ayanami", "Rei_Ayanami_(Gear)", 0.01, 3)
    SpawnItem("Kagamine Len", "Kagamine_Len_(Gear)", 0.01, 3)
    SpawnItem("Rider", "Rider_(Gear)", 0.01, 3)
    SpawnItem("Illyasviel", "Illyasviel_(Gear)", 0.01, 3)
    SpawnItem("EVANGELION Mark.06", "EVANGELION_Mark.06_(Gear)", 0.01, 3)
    SpawnItem("Moca, Noble Maid", "Moca,_Noble_Maid_(Gear)", 0.01,
              3)  # May change to 0.05
    SpawnItem("Sakura Miku x Pixie", "Sakura_Miku_x_Pixie_(Gear)", 0.01, 3)
    SpawnItem("[Club DJ] Himiko", "-Club_DJ-_Himiko_(Gear)", 0.01, 3)

    # Wind SSRs
    # SpawnItem("", "_(Gear)", 0.01, 3)
    SpawnItem("Quetzalcoatl", "Quetzalcoatl_(Gear)", 0.2, 3)
    SpawnItem("Shinatobe, Wind Caller", "Shinatobe,_Wind_Caller_(Gear)", 0.15,
              3)
    SpawnItem("Valkyrie Veere", "Valkyrie_Veere_(Gear)", 0.1, 3)
    SpawnItem("Kirin", "Kirin,_the_Wind_Beast_(Gear)", 0.15, 3)
    SpawnItem("Animus Athena", "Animus_Athena_(Gear)", 0.1, 3)
    SpawnItem("Holiday Hel", "Holiday_Hel_(Gear)", 0.1, 3)
    SpawnItem("Artemis", "Artemis_(Gear)", 0.15, 3)
    SpawnItem("Jupiter", "Jupiter_(Gear)", 0.05, 3)
    SpawnItem("~~TaikunZ's Waifu~~ Yule Merlyn", "Yule_Merlyn_(Gear)", 0.1,
              3)  # May change to 0.05
    SpawnItem("Skuld", "Skuld_(Gear)", 0.05, 3)
    SpawnItem("Sun Wukong", "Sun_Wukong_(Gear)", 0.05, 3)
    SpawnItem("Madoka Kaname", "Madoka Kaname_(Gear)", 0.01, 3)
    SpawnItem("Emilia, Dreamy Magic", "Emilia,_Dreamy_Magic_(Gear)", 0.1, 3)
    SpawnItem("Gaia", "Gaia_(Gear)", 0.1, 3)
    SpawnItem("Eva-01 RT (Vehicle)", "Eva-01_RT_(Vehicle)_(Gear)", 0.01, 3)
    SpawnItem("Mari Makinami I.", "Mari_Makinami_I._(Gear)", 0.01, 3)
    SpawnItem("Hatsune Miku", "Hatsune_Miku_(Gear)", 0.01, 3)
    SpawnItem("Lancer", "Lancer_(Gear)", 0.01, 3)
    SpawnItem("Rin Tohsaka", "Rin_Tohsaka_(Gear)", 0.01, 3)
    SpawnItem("Eva RT2 (F Type C)", "Eva_RT2_(F_Type_C)_(Gear)", 0.01, 3)
    SpawnItem("Eva Unit 08", "Eva_Unit_08_(Gear)", 0.01, 3)
    SpawnItem("Ranmaru", "Ranmaru_(Gear)", 0.01, 3)
    SpawnItem("Feline Kagamine Rin", "Feline_Kagamine_Rin_(Gear)", 0.01, 3)

    # Light SSRs
    # SpawnItem("", "_(Gear)", 0.01, 3)
    SpawnItem("Valkyrie", "Valkyrie_(Gear)", 0.15, 3)  # 0.15 instead of 0.1
    SpawnItem("Indra, Storm God", "Indra,_Storm_God_(Gear)", 0.15, 3)
    SpawnItem("Alice (French Maid)", "Alice_(French_Maid)_(Gear)", 0.01, 3)
    SpawnItem("Nezha", "Nezha_(Gear)", 0.15, 3)
    SpawnItem("Athena", "Athena_(Gear)", 0.1, 3)
    SpawnItem("~~Me!~~ Nyx the Songstress", "Nyx_the_Songstress_(Gear)", 0.1,
              3)
    SpawnItem("Chibi Light Valkyrie", "Chibi_Light_Valkyrie_(Gear)", 0.1, 3)
    SpawnItem("Thor, Divine Guardian", "Thor,_Divine_Guardian_(Gear)", 0.1, 3)
    SpawnItem("Yukino, First Flower", "Yukino,_First_Flower_(Gear)", 0.1, 3)
    SpawnItem("Venus", "Venus_(Gear)", 0.15, 3)
    SpawnItem("Mami Tomoe", "Mami_Tomoe_(Gear)", 0.01, 3)
    SpawnItem("Arthur, the Banneret", "Arthur,_the_Banneret_(Gear)", 0.15, 3)
    SpawnItem("Eva-01", "Eva-01_(Gear)", 0.01, 3)
    SpawnItem("Shinji Ikari", "Shinji_Ikari_(Gear)", 0.01, 3)
    SpawnItem("Eva-01 RT (Sport)", "Eva-01_RT_(Sport)_(Gear)", 0.01, 3)
    SpawnItem("Saber", "Saber_(Gear)", 0.01, 3)
    SpawnItem("[Dress] Saber", "-Dress-_Saber_(Gear)", 0.01, 3)
    SpawnItem("Shirou Emiya", "Shirou_Emiya_(Gear)", 0.01, 3)
    SpawnItem("EVANGELION Mark.09", "EVANGELION_Mark.09_(Gear)", 0.01, 3)
    SpawnItem("Eva RT8 (Sport)", "Eva_RT8_(Sport)_(Gear)", 0.01, 3)
    SpawnItem("Saturn", "Saturn_(Gear)", 0.05, 3)
    SpawnItem("Hatsune Miku x Filo", "Hatsune_Miku_x_Filo_(Gear)", 0.01, 3)

    # Dark SSRs
    # SpawnItem("", "_(Gear)", 0.01, 3)
    SpawnItem("Lilith", "Lilith_(Gear)", 0.2, 3)
    SpawnItem("Casual Style Ninetails", "Casual_Style_Ninetails_(Gear)", 0.01,
              3)
    SpawnItem("Valkyrie Nikyt", "Valkyrie_Nikyt_(Gear)", 0.1, 3)
    SpawnItem("Aizen", "Aizen_(Gear)", 0.15, 3)
    SpawnItem("Anubis the Protector", "Anubis_the_Protector_(Gear)", 0.15, 3)
    SpawnItem("Skotos Athena", "Skotos_Athena_(Gear)", 0.1, 3)
    SpawnItem("Hel", "Hel_(Gear)", 0.15, 3)
    SpawnItem("~~TaikunZ's Waifu~~ Merlyn", "Merlyn_(Gear)", 0.1, 3)
    SpawnItem("Vol & Rena, Young Pirate", "Vol_%26_Rena,_Young_Pirate_(Gear)",
              0.1, 3)  # May change to 0.05
    SpawnItem("Yashamaru", "Yashamaru_(Gear)", 0.05, 3)
    SpawnItem("Thor, Fried Noodle Chef", "Thor,_Fried_Noodle_Chef_(Gear)",
              0.05, 3)
    SpawnItem("Santa Lilith", "Santa_Lilith_(Gear)", 0.01, 3)
    SpawnItem("Emilia, Tyro Witch", "Emilia,_Tyro_Witch_(Gear)", 0.1, 3)
    SpawnItem("HS Student Joan", "HS_Student_Joan_(Gear)", 0.1,
              3)  # May change to 0.05
    SpawnItem("Eva-03", "Eva-03_(Gear)", 0.01, 3)
    SpawnItem("Kaworu Nagisa", "Kaworu_Nagisa_(Gear)", 0.01, 3)
    SpawnItem("Loki, the Trickster", "Loki,_the_Trickster_(Gear)", 0.1, 3)
    SpawnItem("Megurine Luka", "Megurine_Luka_(Gear)", 0.01, 3)
    SpawnItem("Caster", "Caster_(Gear)", 0.01, 3)
    SpawnItem("Assassin", "Assassin_(Gear)", 0.01, 3)
    SpawnItem("Mischievous Mary", "Mischievous_Mary_(Gear)", 0.1, 3)
    SpawnItem("Eva Unit 13", "Eva_Unit_13_(Gear)", 0.01, 3)
    SpawnItem("Stargod Uranus", "Stargod_Uranus_(Gear)", 0.05, 3)
    SpawnItem("Petit Luka", "Petit_Luka_(Gear)", 0.01, 3)

    # Haste SSRs
    # SpawnItem("", "_(Gear)", 0.01, 3)
    SpawnItem("Dragoon Cuchulainn", "Dragoon_Cuchulainn_(Gear)", 0.01, 3)
    SpawnItem("Red Riding Hood", "Red_Riding_Hood_(Gear)", 0.1, 3)
    SpawnItem("Sakuya, Sea Child", "Sakuya,_Sea_Child_(Gear)", 0.1, 3)
    SpawnItem("Catharsis Athena", "Catharsis_Athena_(Gear)", 0.05, 3)
    SpawnItem("Melodic Fiine", "Melodic_Fiine_(Gear)", 0.1, 3)
    SpawnItem("~~The girl who did nothing wrong!~~ Homura Akemi",
              "Homura_Akemi_(Gear)", 0.01, 3)
    SpawnItem("Eva-02 Beast Mode", "Eva-02_Beast_Mode_(Gear)", 0.01, 3)
    SpawnItem("Eva-04", "Eva-04_(Gear)", 0.01, 3)
    SpawnItem("Eva-01 Semi-Awakened", "Eva-01_Semi_Awakened_(Gear)", 0.01, 3)
    SpawnItem("Pseudo DMS Evo. 3", "Pseudo_DMS_Evo._3_(Gear)", 0.01, 3)
    SpawnItem("Tellus", "Tellus_(Gear)", 0.01, 3)
    SpawnItem("Crystal Miku", "Crystal_Miku_(Gear)", 0.01, 3)
    return True


class UnisonOldSpawn:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(aliases=["spawnr"])
    @commands.cooldown(1, 2, BucketType.user)
    async def spawn(self, ctx, amount: int = 1):
        """Brings forth a rush of salt...
        The amount spawned has to be between 1 and 10 inclusive.

        Dedicated to our old friend RusyChicken, who had the original RNGesus
        spawning bot.
        """
        if amount < 1 or amount > 10:
            await reply(ctx, "WTF?!")
            ctx.command.reset_cooldown(ctx)
            return
        msg = await ctx.channel.send("Spawning...\n:large_blue_circle: >>>>")
        spawn_ten = amount == 10
        spawned = []
        top_rank = 0
        for i in range(0, amount):
            spawn = things[randint(0, len(things) - 1)]
            spawned.append(spawn)
            top_rank = max(top_rank, spawn.rank)
        await asyncio.sleep(1)
        if top_rank == 1 and not spawn_ten:
            await msg.edit(
                content="Spawning...\n:large_blue_circle: >>>>>>>> " + emoji[
                    1])
        else:
            await msg.edit(content=" ".join(
                ["Spawning...\n:large_blue_circle: >>>>>>>>", emoji[1],
                 ">>>>"]))
            if spawn_ten and top_rank == 1:
                spawned[randint(0, len(spawned) - 1)] = pity[
                    randint(0, len(pity) - 1)]
                top_rank = 2
            await asyncio.sleep(1)
            if top_rank == 2:
                await msg.edit(content=" ".join(
                    ["Spawning...\n:large_blue_circle: >>>>>>>>", emoji[1],
                     ">>>>>>>>", emoji[2]]))
            else:
                await msg.edit(content=" ".join(
                    ["Spawning...\n:large_blue_circle: >>>>>>>>", emoji[1],
                     ">>>>>>>>", emoji[2], ">>>>"]))
                await asyncio.sleep(1)
                await msg.edit(content=" ".join(
                    ["Spawning...\n:large_blue_circle: >>>>>>>>", emoji[1],
                     ">>>>>>>>", emoji[2], ">>>>>>>>", emoji[3]]))
        await asyncio.sleep(1)
        if amount > 1:
            decor = ["Spawning:\n"]
            for spawn in spawned:
                decor.append(emoji[spawn.rank] + " ")
            await msg.edit(content="".join(decor).strip())
            await asyncio.sleep(2)
        await msg.delete()
        if amount > 1:
            msg = ["Congratulations! You spawned the following:"]
            top_url = None
            for spawn in spawned:
                msg.append("".join(["\n", spawn.name, " (", ranks[spawn.rank],
                                    ") at " + (
                                        "%.2f" % (
                                            spawn.prob * 10000 / len(things))),
                                    "% probability."]))
                if spawn.rank == 3:
                    msg.extend(["\n", url_prefix, spawn.url])
                elif top_rank == spawn.rank:
                    top_url = "".join(["\n", url_prefix, spawn.url])
            if top_url is not None:
                msg.append(top_url)
            msg = "".join(msg)
        else:
            spawned = spawned[0]
            msg = "".join(["Congratulations! You spawned ", spawned.name, " (",
                           ranks[spawned.rank], ") at ",
                           ("%.2f" % (spawned.prob * 10000 / len(things))),
                           "% probability.\n", url_prefix, spawned.url])
        await reply(ctx, msg)


def setup(nyx):
    load()
    nyx.add_cog(UnisonOldSpawn(nyx))
