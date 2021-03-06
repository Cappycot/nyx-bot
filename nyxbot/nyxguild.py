"""Default loader for guild-specific data."""

from configparser import ConfigParser, ParsingError
from os import getcwd, listdir, mkdir
from os.path import isfile, join, exists

from discord.ext import commands
from discord.ext.commands import Cog

import nyxbot.nyxcommands as nyxcommands
from nyxbot.nyxdata import GuildData
from nyxbot.nyxutils import list_string, reply

default_folder = "guilds"
is_manager = nyxcommands.has_privilege_or_permissions(privilege=-1,
                                                      manage_server=True)
prefix_add_alias = ["a", "add"]
prefix_rem_alias = ["d", "del", "r", "rem", "remove"]


class NyxGuild(Cog):
    def __init__(self, nyx):
        self.folder = default_folder
        self.nyx = nyx
        # self.load_all_guild_data()
        # Test of saving...
        # gd = GuildData(1234)
        # self.nyx.guild_data[1234] = gd
        # gd.modules = ["unison"]
        # gd.prefixes = []
        # self.save_guild_data(1234)

    def load_guild_data(self, gid, path=None):
        guild_data = GuildData(int(gid))
        self.nyx.guild_data[int(gid)] = guild_data
        # Can specify external path for guild's data if needed.
        if path is None:
            path = join(getcwd(), self.folder, str(gid))
        config = ConfigParser()
        with open(path) as file:
            config.read_file(file)
            if "Settings" in config:
                settings = config["Settings"]
                # print(guild_data.modules)
                # Get modules that have been imported into the guild.
                if "Modules" in settings and settings["Modules"]:
                    # guild_data.modules.extend(
                    # settings["Modules"].split(" "))
                    for module_name in settings["Modules"].split():
                        print(module_name)
                        print(guild_data.import_module(self.nyx, module_name))
                # print(guild_data.modules)
                # Get prefixes that the guild uses.
                if "Prefixes" in settings and settings["Prefixes"]:
                    guild_data.prefixes.extend(
                        settings["Prefixes"].split(" "))
            # Set other guild data that other modules may have created.
            if "Data" in config:
                data = config["Data"]
                for key in data:
                    guild_data.data[key] = data.get(key, None)

    def load_all_guild_data(self, folder: str = None, path: str = None):
        if folder is not None:
            self.folder = folder
        elif self.nyx.guilds_folder is not None:
            self.folder = self.nyx.guilds_folder
        if path is None:
            path = join(getcwd(), self.folder)
        # Folder checks.
        if not exists(path):
            mkdir(path)
            print(
                "New {} directory created for guild data.".format(self.folder))
            return True
        elif isfile(path):
            print("Cannot use {} for guild data; blocked by file.".format(
                self.folder))
            return False
        # Load guild data for all files found.
        for gid in listdir(path):
            guild_path = join(path, gid)
            if not isfile(guild_path):
                continue
            try:
                self.load_guild_data(gid, guild_path)
            except ValueError:
                # Ignore files that don't have guild id names.
                pass
            except ParsingError:
                print("Guild with ID " + gid + " failed to parse.")
        return True

    def save_guild_data(self, gid, path=None):
        guild_data = self.nyx.guild_data.get(int(gid), GuildData(int(gid)))
        if path is None:
            path = join(getcwd(), self.folder, str(gid))
        config = ConfigParser()
        modules = " ".join(guild_data.modules)
        prefixes = " ".join(guild_data.prefixes).replace("%", "%%")
        config["Settings"] = {"Modules": modules, "Prefixes": prefixes}
        config["Data"] = {}
        for key in guild_data.data:
            config["Data"][key] = guild_data.data[key]
        with open(path, "w") as file:
            config.write(file)

    def save_all_guild_data(self):
        if self.nyx.guilds_folder is not None:
            self.folder = self.nyx.guilds_folder
        if self.folder is None:
            return False
        for gid in self.nyx.guild_data:
            self.save_guild_data(gid)

    async def list_modules(self, ctx):
        """Replies with the list of modules on the server."""
        guild_data = self.nyx.get_guild_data(ctx.message.guild)
        plural = len(guild_data.modules) > 1
        result = list_string(guild_data.modules)
        await self.nyx.reply(ctx, "".join(["Module", "s" if plural else "",
                                           " for this server ",
                                           "are " if plural else "is ",
                                           result]))

    @commands.group(aliases=["modules"])
    async def module(self, ctx):
        """List, add, or remove modules from a server."""
        if ctx.invoked_subcommand is None:
            await self.list_modules(ctx)

    @module.command(name="add", aliases=["a", "i", "import"])
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def module_add(self, ctx, *modules):
        """Adds modules to the server."""
        if len(modules) == 0:
            await self.nyx.reply(ctx,
                                 "You didn't tell me what modules to add!")
            return
        guild_data = self.nyx.get_guild_data(ctx.message.guild)
        changed = []
        for mod in modules:
            if guild_data.import_module(self.nyx, mod):
                changed.append(mod)
        if len(changed) == 0:
            await self.nyx.reply(ctx, " ".join(["Either the modules were",
                                                "already added or I couldn't",
                                                "find them..."]))
        else:
            self.save_guild_data(guild_data.id)
            await reply(ctx, "Added module(s) " + list_string(changed))

    @module.command(name="list")
    @commands.guild_only()
    async def module_list(self, ctx):
        """Lists the modules on the server."""
        await self.list_modules(ctx)

    @module.command(name="remove",
                    aliases=["d", "del", "deport", "r", "rem", "rm"])
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def module_remove(self, ctx, *modules):
        """Removes modules from the server."""
        if len(modules) == 0:
            await self.nyx.reply(ctx,
                                 "You didn't tell me what modules to remove!")
            return
        guild_data = self.nyx.get_guild_data(ctx.message.guild)
        changed = []
        for mod in modules:
            if guild_data.deport_module(self.nyx, mod):
                changed.append(mod)
        if len(changed) == 0:
            await self.nyx.reply(ctx, " ".join(
                ["I couldn't find such a", "module to remove."]))
        else:
            self.save_guild_data(guild_data.id)
            await reply(ctx, "Removed module(s) " + list_string(changed))

    @commands.command(aliases=["prefixes"])
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def prefix(self, ctx, action=None, *prefixes):
        """List, add, or remove prefixes from a server."""
        add = False
        remove = False
        if action is not None:
            add = any(action == a for a in prefix_add_alias)
            remove = not add and any(action == a for a in prefix_rem_alias)
        guild_data = self.nyx.get_guild_data(ctx.message.guild)
        if add or remove:
            if is_manager(ctx):
                if len(prefixes) == 0:
                    await reply(ctx, "You didn't tell me what prefixes to " +
                                ("add!" if add else "remove!"))
                    return
                changed = []
                for prefix in prefixes:
                    if add and prefix not in guild_data.prefixes:
                        guild_data.prefixes.append(prefix)
                        changed.append(prefix)
                    elif remove and prefix in guild_data.prefixes:
                        guild_data.prefixes.remove(prefix)
                        changed.append(prefix)
                if len(changed) == 0:
                    if add:
                        await reply(ctx, "The prefixes were already added.")
                    else:
                        await reply(ctx, "I couldn't find such a " +
                                    "prefix to remove.")
                else:
                    self.save_guild_data(guild_data.id)
                    result = ("Added" if add else "Removed") + " prefix(es) "
                    result += list_string(changed, key=lambda a: "'" + a + "'")
                    await reply(ctx, result)
            else:
                await reply(ctx, "You don't have permission to change this " +
                            "guild's prefixes.")
        elif len(guild_data.prefixes) == 0:
            await reply(ctx, "This guild has no set prefixes...")
        else:
            plural = len(guild_data.prefixes) > 1
            result = list_string(guild_data.prefixes,
                                 key=lambda a: "'" + a + "'")
            await reply(ctx, "Prefix" + ("es" if plural else "") +
                        " for this server " + (
                            "are " if plural else "is ") + result)
