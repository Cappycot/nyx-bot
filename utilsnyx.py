
# Binary search with lambdas woo fucking hoo!
def binary_search(array, query, key = lambda a: a):
    if array is None or len(array) == 0:
        return None
    elif len(array) == 1:
        return key(array[0]) == query and array[0] or None
    mid = int(len(array) / 2)
    compare_to = key(array[mid])
    if query < compare_to:
        return binary_search(array[:mid], query, key)
    elif query > compare_to:
        return binary_search(array[mid + 1:], query, key)
    else:
        return array[mid]


# Prints a list in legible format
def list_string(alist, key = lambda a: a):
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


# Prunes Discord bots from a list of users
def remove_bots(alist, key = lambda a: a):
    i = 0
    while i < len(alist):
        if key(alist[i]).bot:
            alist.remove(alist[i])
        else:
            i += 1
