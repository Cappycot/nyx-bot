from nyx.nyxdata import GuildData, UserData


class NyxBase:
    def __init__(self, default_cog_name):
        self.default_cog_name = default_cog_name

        # The disambiguation table is used to look up commands of the same
        # name, distinguished by the object id.
        self.disambiguations = {}  # {command name:{object id:command}}

        # The namespaces table is used to look up commands by the cog name.
        self.namespaces = {}  # {cog name:{command name:command}}

        self.guild_cog = None
        self.guild_data = {}
        self.guilds_folder = None
        self.user_cog = None
        self.user_data = {}
        self.users_folder = None

    def get_disambiguation(self, name, create=False):
        """Get the dict of cogs that have a command with such a name. This is
        case-insensitive.
        """
        name = name.lower()
        if create and name not in self.disambiguations:
            self.disambiguations[name] = {}
        return self.disambiguations.get(name, None)

    def get_namespace(self, name, create=False):
        """Get the dict of commands from a cog of a certain name. This is case-
        insensitive.
        """
        if name is not None:
            name = name.lower()
            if name == "none":
                name = None
        if create and name not in self.namespaces:
            self.namespaces[name] = {}
        return self.namespaces.get(name, None)

    def add_command_entry(self, command):
        cog_name = command.cog_name
        self.get_disambiguation(command.name.lower(), create=True)[
            id(command)] = command
        namespace = self.get_namespace(cog_name, create=True)
        namespace[command.name.lower()] = command
        # Add aliases to disambiguations and namespace.
        for alias in command.aliases:
            self.get_disambiguation(alias.lower(), create=True)[
                id(command)] = command
            namespace[alias.lower()] = command

    def remove_disambiguation_command(self, command_name, command):
        disambiguation = self.get_disambiguation(command_name)
        if disambiguation is not None:
            return disambiguation.pop(id(command), None)
        # if command_name not in command.aliases:
        # for alias in command.aliases:
        # self.get_disambiguation(alias).pop(id(command), None)
        return None

    def remove_namespace_command(self, command_name, cog_name):
        namespace = self.get_namespace(cog_name)
        if namespace is not None:
            return namespace.pop(command_name, None)
        return None

    def get_guild_data(self, discord_guild):
        """Retrieves the GuildData object for a particular Discord Guild. If
        such GuildData does not exist, then create a new object to hold
        data. This is guaranteed to never return None unless None is passed
        as an argument.
        """
        if discord_guild is None:
            return None
        # Since both Discord Guild and GuildData have a integer id
        # parameter, this will still be okay if GuildData is passed.
        # Quack quack.
        elif discord_guild.id not in self.guild_data:
            self.guild_data[discord_guild.id] = GuildData(discord_guild.id)
        return self.guild_data[discord_guild.id]

    def get_user_data(self, discord_user):
        """Retrieves the UserData object for a particular Discord User. If such
        UserData does not exist, then create a new object to hold data. This is
        guaranteed to never return None unless None is passed as an argument.
        """
        if discord_user is None:
            return None
        # Quack quack.
        if discord_user.id not in self.user_data:
            self.user_data[discord_user.id] = UserData(discord_user.id)
        return self.user_data[discord_user.id]
