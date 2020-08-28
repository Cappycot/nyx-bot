from discord.ext.commands import Cog


class GuildData:
    """Class for holding preference data for Discord guilds
    in terms of custom modules imported and prefixes to use.
    """

    def __init__(self, guild_id: int):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = guild_id
        self.command_map = {}
        self.data = {}
        self.modules = []
        self.prefixes = []

    def check_collision(self, namespace: dict):
        for name in namespace:
            if name in self.command_map and self.command_map[name] is not None:
                return name
        return None

    # TODO: Revise guild module import system.
    def import_module(self, nyx, mod):
        mod = mod.lower()
        if mod in self.modules:
            return False
        namespace = nyx.get_namespace(mod)
        if namespace is None:
            return False
        if self.check_collision(namespace) is not None:
            return False
        self.modules.append(mod)
        for name in namespace:
            self.command_map[name] = namespace[name]
        return True

    def map_commands(self, nyx):
        self.command_map = {}
        passed_modules = []
        for mod in self.modules:
            namespace = nyx.get_namespace(mod)
            if namespace is None:
                continue
            if self.check_collision(namespace) is not None:
                continue
            for name in namespace:
                self.command_map[name] = namespace[name]
            passed_modules.append(mod)
        self.modules = passed_modules

    def deport_module(self, nyx, mod):
        mod = mod.lower()
        if mod not in self.modules:
            return False
        self.modules.remove(mod)
        # For the record, I did consider lazy deletion, but there may come a
        # time in the future when namespaces can be modified, so map_commands
        # is a good thing to have around.
        self.map_commands(nyx)
        return True


class UserData:
    """Class for storing specific data for a Discord user.
    Only the user ID of a Discord User is stored between
    sessions outside of permissions and module-specific data.
    """

    def __init__(self, user_id: int):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = user_id
        self.data = {"privilege": 1}

    @property
    def privilege(self):
        return self.data["privilege"]

    def get_privilege(self):
        return self.data["privilege"]

    def set_privilege(self, level: int):
        self.data["privilege"] = level
