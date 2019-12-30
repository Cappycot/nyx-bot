class NyxDisambiguation:
    def __init__(self):
        self.disambiguations = {}

    def get_disambiguation(self, name, create=False):
        """Get the dict of cogs that have a command with such a name. This is
        case-insensitive.
        """
        name = name.lower()
        if create and name not in self.disambiguations:
            self.disambiguations[name] = {}
        return self.disambiguations.get(name, None)

    def add_command(self, command):
        self.get_disambiguation(command.name.lower(), create=True)[
            id(command)] = command
        for alias in command.aliases:
            self.get_disambiguation(alias.lower(), create=True)[
                id(command)] = command

    def get_command(self, command_name):
        disambiguation = self.get_disambiguation(command_name)
        if disambiguation is None or len(disambiguation) > 1:
            return None
        return list(disambiguation.values())[0]

    def remove_command(self, command_name, command):
        disambiguation = self.get_disambiguation(command_name)
        if disambiguation is not None:
            return disambiguation.pop(id(command), None)
        # if command_name not in command.aliases:
        # for alias in command.aliases:
        # self.get_disambiguation(alias).pop(id(command), None)
        return None
