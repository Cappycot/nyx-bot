class NyxNamespace:
    def __init__(self, default_cog_name=None):
        self.default_cog_name = default_cog_name
        self.namespaces = {}  # {cog name:{command name:command}}

    def get_namespace(self, name, create=False):
        """Get the dict of commands from a cog of a certain name. This is case-
        insensitive.
        """
        if name is not None:
            name = name.lower()
        if create and name not in self.namespaces:
            self.namespaces[name] = {}
        return self.namespaces.get(name, None)

    def add_command(self, command):
        cog_name = command.cog_name
        namespace = self.get_namespace(cog_name, create=True)
        namespace[command.name.lower()] = command

    # TODO: Fix None case.
    def get_command(self, command_name):
        command_name = command_name.lower()
        command = None
        for namespace in self.namespaces.values():
            for name in namespace:
                if command_name == name:
                    if command is not None:
                        return None
                    command = namespace[name]
        return command

    def get_command(self, command_name, cog_name):
        namespace = self.get_namespace(cog_name)
        if namespace is None:
            return None
        return namespace.get(command_name.lower(), None)

    def remove_command(self, command_name, cog_name):
        namespace = self.get_namespace(cog_name)
        if namespace is not None:
            return namespace.pop(command_name, None)
        return None
