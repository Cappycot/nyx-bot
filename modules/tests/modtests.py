###############################################################################
# Python Library Concept Tests
###############################################################################

import asyncio
import io
import os
from PIL import Image
import urllib3
from sys import exc_info

http = urllib3.PoolManager()
testdir = None


###############################################################################
# Command Functions
###############################################################################

async def obliterate(client = None, message = None, **_):
    """Concept test of PIL usage and image editing..."""
    
    # Check to make sure everything is there.
    if client is None or message is None:
        return "Our tank disappeared, sir!"
    elif len(message.mentions) != 1 or message.server is None:
        return "We couldn't get a target, sir!"
    elif message.mentions[0] == client.user:
        return "I'm your gunner you moron..."
    elif message.author == message.mentions[0]:
        return "What? Do you have crippling depression?"
    
    # Get both users
    shooter = message.author
    victim = message.mentions[0]
    
    global testdir
    try:
        # Get urls for profile pics
        url2 = victim.avatar_url
        if not url2:
            url2 = victim.default_avatar_url
        url1 = shooter.avatar_url
        if not url1:
            url1 = shooter.default_avatar_url
        
        # Presets for image creation
        avatarside = 80
        spos = (130, 42)
        vpos = (260, 360)
        
        # Make http request for profile pictures and get background tank
        shooter = Image.open(io.BytesIO(http.request("GET", url1).data))
        victim = Image.open(io.BytesIO(http.request("GET", url2).data))
        backdrop = Image.open(testdir + "/Obliterate.png")
        
        # Paste shooter on top of tank as resized image
        shooter = shooter.resize((avatarside, avatarside), Image.LANCZOS)
        backdrop.paste(shooter, (spos[0], spos[1],
                        spos[0] + avatarside, spos[1] + avatarside))
        
        # Rotate victim and clear out black noise
        victim = victim.resize((avatarside, avatarside), Image.LANCZOS)
        victim = victim.rotate(-40, expand = True)
        vw = victim.size[0]
        vh = victim.size[1]
        vback = Image.new("RGB", (512, 512), (0, 0, 0))
        vback.paste(victim, (vpos[0], vpos[1], vpos[0] + vw, vpos[1] + vh))
        victim = vback.getdata()
        backdata = backdrop.getdata()
        mixdata = []
        for i in range(0, len(victim)):
            item = victim[i]
            if item[0] + item[1] + item[2] == 0:
                mixdata.append(backdata[i])
            else:
                red = min(item[0] + 42, 255)
                green = min(item[1] + 9, 255)
                blue = max(item[2] - 9, 0)
                mixdata.append((red, green, blue))
        
        # Put it all together
        backdrop.putdata(mixdata)
        testpic = io.BytesIO()
        backdrop.save(testpic, format="png") # Save bytes to stream.
        testpic.seek(0) # Move pointer to beginning so Discord can read pic.
        await client.send_file(message.channel, testpic, filename = "kill.png")
        return "Another one bites the dust! ``*CLAP*``"
    except:
        err = exc_info()
        for e in err:
            print(e)
        return "Uhh... we misfired, sir!"


commands = [[["obliterate", "destroy", "pwn"], obliterate, "Reks a user.", "obliterate @user", -1]]


def init(module = None, **_):
    if module is None:
        return False
    global testdir
    testdir = module.folder
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    module.make_primary()
    return True




