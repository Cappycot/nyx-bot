"""Default loader for user-specific data."""

from configparser import ConfigParser, ParsingError
from discord.ext import commands
from nyx import UserData
from os import getcwd, listdir
from os.path import isfile, join

default_folder = "users"


class User:
    def __init__(self, nyx):
        self.folder = default_folder
        self.nyx = nyx
        self.load_all_user_data()
        # Test of saving...
        # ud = UserData(1234)
        # self.nyx.user_data[1234] = ud
        # ud.set_privilege(-2)
        # ud.data["Test"] = "test"
        # self.save_user_data(1234)

    def load_user_data(self, uid, path=None):
        user_data = UserData(int(uid))
        self.nyx.user_data[int(uid)] = user_data
        if path is None:
            path = join(getcwd(), self.folder, str(uid))
        config = ConfigParser()
        with open(path) as file:
            config.read_file(file)
            if "Privilege" in config and "privilege" in config["Privilege"]:
                user_data.set_privilege(int(config["Privilege"]["privilege"]))
            if "Data" in config:
                data = config["Data"]
                for key in data:
                    if key == "privilege":
                        # Avoid setting int value to a string.
                        continue
                    user_data.data[key] = data.get(key, None)

    def load_all_user_data(self):
        if self.nyx.users_folder is not None:
            self.folder = self.nyx.users_folder
        if self.folder is None:
            return False
        path = join(getcwd(), self.folder)
        for uid in listdir(path):
            user_path = join(path, uid)
            if not isfile(user_path):
                continue
            try:
                self.load_user_data(uid, user_path)
            except ValueError:
                # Ignore files that don't have user id names.
                pass
            except ParsingError:
                print("User with ID " + uid + " failed to parse.")
        return True

    def save_user_data(self, uid, path=None):
        user_data = self.nyx.user_data.get(int(uid), UserData(int(uid)))
        if path is None:
            path = join(getcwd(), self.folder, str(uid))
        config = ConfigParser()
        config["Privilege"] = {"privilege": user_data.get_privilege()}
        config["Data"] = {}
        for key in user_data.data:
            if key == "privilege":
                # Privilege was already fetched to elsewhere.
                continue
            print(key)
            config["Data"][key] = user_data.data[key]
        with open(path, "w") as file:
            config.write(file)

    def save_all_user_data(self):
        if self.nyx.users_folder is not None:
            self.folder = self.nyx.users_folder
        if self.folder is None:
            return False
        for uid in self.nyx.user_data:
            self.save_user_data(uid)


def setup(bot):
    bot.add_cog(User(bot))
