"""
This is a simple file that can run Nyx. It will take the token from the
info.nyx (or whatever config) file and use it to start your Discord bot up.
The name of the folder where cogs are stored can be specified here as well.
"""

from configparser import ConfigParser
from nyx import Nyx

nyx_cog_folder = "cogs"  # The folder where cogs will be searched for.
nyx_config_file = "info.nyx"  # The name of the config file used.

nyx = Nyx()
nyx.load_cogs(nyx_cog_folder)  # Get cogs from specified folder.

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
