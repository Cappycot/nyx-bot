"""Default loader for user-specific data."""

from configparser import ConfigParser, ParsingError
from os import getcwd, listdir, mkdir
from os.path import isfile, join, exists

# from discord.ext import commands
from nyx.nyxdata import UserData

default_folder = "users"


class NyxUser:
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
        # Can specify external path for user's data if needed.
        if path is None:
            path = join(getcwd(), self.folder, str(uid))
        config = ConfigParser()
        with open(path) as file:
            config.read_file(file)
            # Set user privilege value.
            if "Privilege" in config and "privilege" in config["Privilege"]:
                user_data.set_privilege(int(config["Privilege"]["privilege"]))
            # Set other user data that other modules may have created.
            if "Data" in config:
                data = config["Data"]
                for key in data:
                    if key == "privilege":
                        # Avoid setting int value to a string.
                        continue
                    user_data.data[key] = data.get(key, None)

    def load_all_user_data(self, folder: str=None, path: str=None):
        if folder is not None:
            self.folder = folder
        elif self.nyx.users_folder is not None:
            self.folder = self.nyx.users_folder
        if path is None:
            path = join(getcwd(), self.folder)
        # Folder checks.
        if not exists(path):
            mkdir(path)
            print(
                "New {} directory created for user data.".format(self.folder))
            return True
        elif isfile(path):
            print("Cannot use {} for user data; blocked by file.".format(
                self.folder))
            return False
        # Load user data for all files found.
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
