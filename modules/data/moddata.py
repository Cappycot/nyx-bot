###############################################################################
# Practice for CS 3345
###############################################################################

import asyncio
from simplelist import SimpleStruct
from sys import exc_info
from trees import Tree
from avltrees import AVLTree
from rbtrees import RBTree

min_value = 0
max_value = 999
structs = {}

def get_data(user_id):
    global structs
    if user_id in structs:
        return structs[user_id]
    else:
        struct = SimpleStruct()
        structs[user_id] = struct
        return struct
        

###############################################################################
# Command Functions
###############################################################################

async def insert(message = None, **_):
    if message is None:
        return "Failed!"
    args = message.content.split(" ")
    element = 0
    try:
        element = int(args[1])
        if element < 0 or element > max_value:
            return "The integer must between 0 and " + str(max_value) + " (inclusive)."
    except:
        return "Specify an integer to insert."
    struct = get_data(message.author.id)
    return struct.insert(element)


async def remove(message = None, **_):
    if message is None:
        return "Failed!"
    args = message.content.split(" ")
    element = 0
    try:
        element = int(args[1])
        if element < 0 or element > max_value:
            return "The integer must between 0 and " + str(max_value) + " (inclusive)."
    except:
        return "Specify an integer to remove."
    struct = get_data(message.author.id)
    return struct.remove(element)


async def reset(message = None, **_):
    if message is None:
        return "Failed!"
    global structs
    structs[message.author.id] = SimpleStruct()
    return "All data cleared."


async def output(message = None, **_):
    if message is None:
        return "Failed!"
    return get_data(message.author.id).output()


async def changerbtree(message = None, **_):
    if message is None:
        return "Failed!"
    global structs
    struct = get_data(message.author.id)
    if "RBTree" in struct.type:
        return "Your structure is already in Red-black Tree form!"
    newtree = RBTree(Tree)
    newtree.data = struct.data
    newtree.restructure_data()
    structs[message.author.id] = newtree
    return "Attempted to change data set into a Red-black Tree."


commands = [[["add", "ins"], insert, "Inserts an element into the current data structure.", "insert <int>", 1],
            [["del", "rem"], remove, "Removes element from current data structure.", "remove <int>", 1],
            [["reset", "clean"], reset, "Reset data structure.", "reset", 1],
            [["print", "output"], output, "Output data structure.", "output", 1],
            [["rbtree"], changerbtree, "Changes data structure to a Red-black Tree.", "rbtree", 1]]


###############################################################################
# Event Functions
###############################################################################

async def clock(client = None, time = None, **_):
    pass


###############################################################################
# Module Functions
###############################################################################

def init(module = None, loadstring = None, **_):
    if module is None:
        return False
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    module.set_listener(clock, "clock")
    return True




