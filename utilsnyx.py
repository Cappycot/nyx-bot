
# Binary search with lambda parameter
def binary_search(array, query, key = lambda a: a, start = 0, end = -1):
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
    # mid = int(start + (end - start) / 2)
    # print(mid)
    
    # mid = int(len(array) / 2)
    compare_to = key(array[mid]) # Applies lambda to array items.
    if query < compare_to:
        return binary_search(array, query, key, start, mid)
    elif query > compare_to:
        return binary_search(array, query, key, mid + 1, end)
    else:
        return array[mid]


# Prints a list in legible format
def list_string(alist, key = lambda a: a):
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


# Prunes Discord bots from a list of users
def remove_bots(alist, key = lambda a: a):
    i = 0
    while i < len(alist):
        if key(alist[i]).bot:
            alist.remove(alist[i])
        else:
            i += 1
