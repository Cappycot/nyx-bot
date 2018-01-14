from configparser import ConfigParser
from nyx import Nyx

nyx_cog_folder = "cogs"
nyx_config_file = "info.nyx"

nyx = Nyx()
nyx.load_cogs(nyx_cog_folder)

nyx_config = ConfigParser()
nyx_config.read(nyx_config_file)
# If the file doesn't exist ConfigParser will just read empty.
if "Settings" not in nyx_config:
    print("Settings not found. Configure your " +
          nyx_config_file + " file.")
elif "Token" not in nyx_config["Settings"]:
    print("Token setting not found. Configure your " +
          nyx_config_file + " file.")
else:
    nyx.run(nyx_config["Settings"]["Token"])
