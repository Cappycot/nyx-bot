###############################################################################
# Practice for CS 3345
###############################################################################

import asyncio
from simplelist import SimpleStruct
from sys import exc_info
from trees import Tree
from avltrees import AVLTree
from rbtrees import RBTree
from heaps import MaxHeap
from utilsnyx import list_string

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
    if len(args) < 2:
        return "Specify integers to insert (space-separated)."
    inserted = []
    struct = get_data(message.author.id)
    for i in range(1, len(args)):
        try:
            element = int(args[i])
            if element >= min_value and element <= max_value and struct.insert(element):
                inserted.append(element)
        except:
            e = exc_info()
            for a in e:
                print(a)
    if len(inserted) < 1:
        if struct.size == struct.max_elements:
            return "We inserted the max amount of elements already..."
        return "Specify integers between 0-999 to insert..."
    succtext = "I inserted " + list_string(inserted) + "."
    if struct.size == struct.max_elements:
        succtext += " Some couldn't be inserted because we hit the max amount."
    return succtext


async def remove(message = None, **_):
    if message is None:
        return "Failed!"
    struct = get_data(message.author.id)
    if "Heap" in struct.type:
        removed = struct.delete_min()
        return str(removed) + " removed." if removed is not None else "There was nothing to remove..."
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


async def size(message = None, **_):
    if message is None:
        return "Failed"
    struct = get_data(message.author.id)
    entries = struct.size
    sname = struct.type
    return "You have " + str(entries) + " element" + ("s" if entries != 1 else "") + " inserted in type " + sname + "."


async def output(message = None, **_):
    if message is None:
        return "Failed!"
    return get_data(message.author.id).output()
    

def normalize_data(struct):
    if "Tree" in struct.type:
        struct.move_to_data()
    elif "Heap" in struct.type:
        struct.data = struct.data[1:]


async def changerbtree(message = None, **_):
    if message is None:
        return "Failed!"
    global structs
    struct = get_data(message.author.id)
    if "Red-black Tree" in struct.type:
        return "Your structure is already in Red-black Tree form!"
    normalize_data(struct)
    newtree = RBTree(Tree)
    newtree.data = struct.data
    newtree.restructure_data()
    newtree.data = []
    structs[message.author.id] = newtree
    return "Attempted to change data set into a Red-black Tree."


async def heapify(message = None, **_):
    if message is None:
        return "Failed!"
    global structs
    struct = get_data(message.author.id)
    normalize_data(struct)
    newheap = MaxHeap(SimpleStruct)
    newheap.data.extend(struct.data)
    newheap.size = struct.size
    # print(newheap.data)
    newheap.heapify()
    structs[message.author.id] = newheap
    return "Attempted to change data set into a max heap."


commands = [[["add", "ins"], insert, "Inserts an element into the current data structure.", "insert <int>", 1],
            [["del", "rem"], remove, "Removes element from current data structure.", "remove <int>", 1],
            [["print", "output"], output, "Output data structure.", "output", 1],
            [["reset", "clean", "clear"], reset, "Reset data structure.", "reset", 1],
            [["size", "length"], size, "Shows the number of entries.", "size", 1],
            [["rbtree"], changerbtree, "Changes data structure to a Red-black Tree.", "rbtree", 1],
            [["heap", "maxheap"], heapify, "Changes data structure to a max heap.", "heap", 1]]


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




