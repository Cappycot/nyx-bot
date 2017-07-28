from discord.ext.commands import BadArgument
from discord.ext.commands.converter import MemberConverter


def binary_search(array, query, key=lambda a: a, start=0, end=-1):
    """Python's 'in' keyword performs a linear search on arrays.
    Given the circumstances of storing sorted arrays, it's better
    for Nyx to use a binary search.
    
    Arguments:
    key - filter for objects in the array
    start - 0-indexed starting marker on the array to search
    end - exclusive ending marker on the array to search
    """
    if array is None or len(array) == 0:
        return None
        # elif len(array) == 1:
        # return key(array[0]) == query and array[0] or None

    if end == -1:
        end = len(array)
    elif start >= end:
        return None

    # print(start, "and", end)
    mid = int(start + (end - start) / 2)
    # print(mid)

    # mid = int(len(array) / 2)
    compare_to = key(array[mid])  # Applies lambda to array items.
    if query < compare_to:
        return binary_search(array, query, key, start, mid)
    elif query > compare_to:
        return binary_search(array, query, key, mid + 1, end)
    else:
        return array[mid]


member_converter = MemberConverter()


async def get_member(ctx, query):
    try:
        return await member_converter.convert(ctx, query)
    except BadArgument:
        return None


# Prints a list in legible format
def list_string(alist, key=lambda a: a):
    """Given items a, b, ..., x, y, z in an array,
    this will print "a, b, ..., x, y and z"
    """
    if len(alist) == 0:
        return "[empty]"
    elif len(alist) < 2:
        return str(key(alist[0]))
    elif len(alist) == 2:
        return str(key(alist[0])) + " and " + str(key(alist[1]))
    result = ""
    count = 0
    for item in alist:
        count += 1
        if count == len(alist):
            result += "and " + str(key(item))
        else:
            result += str(key(item)) + ", "
    return result


def print_line():
    """Print a line of 80 dashes."""
    print("-" * 80)


def remove_bots(alist, key=lambda a: a):
    """Prunes Discord bots from a list of users."""
    i = 0
    while i < len(alist):
        if key(alist[i]).bot:
            alist.remove(alist[i])
        else:
            i += 1


async def reply(ctx, content):
    if ctx.message.guild is None:
        return await ctx.send(content)
    else:
        return await ctx.send("{}, {}".format(ctx.author.mention, content))


async def respond(ctx, content):
    return await reply(ctx, content)


def trim(string):
    """Removes all carriage returns, newlines, and spaces from the
    target string. Not sure how much this operation costs.
    """
    while string[-1:] == "\r" or string[-1:] == "\n":
        string = string[:-1].strip()
    return string
