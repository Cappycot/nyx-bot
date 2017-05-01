########################################################################
# /r/unexpectedfactorial
########################################################################
# Honestly, this was some decent practice with regex...

from math import ceil, factorial, floor, log, pi
from re import findall, match, search

ram_constant = log(pi) / 2
decimal_past = 9999999999999999 # 16 9s, I guess...
estimate_past = 10000
length_limit = 100
max_mentions = 8


########################################################################
# Factorial Functions
########################################################################

def get_factorial(figure):
    num = figure[1]
    if num <= estimate_past:
        # Get direct factorial of number...
        result = factorial(num)
        if result > decimal_past:
            power = ceil(log(result, 10))
            result = floor(result / (10 ** (power - 4)) + 0.5)
            if result >= 10000:
                result /= 10000
            else:
                result /= 1000
                power -= 1
            return "! ≈ " + figure[0] + str(result) + "x10^" + str(power)
        else:
            return "! = " + figure[0] + str(result)
    else:
        # Use Srinivasa Ramanujan's Approximation
        exp = num * (log(num) - 1) + ram_constant
        exp += log(num + 4 * num ** 2 + 8 * num ** 3) / 6
        # Change base to 10 from e.
        exp = int(exp / log(10))
        # Create a new base 10 exp if necessary...
        if exp > decimal_past:
            power = ceil(log(exp, 10))
            exp = floor(exp / (10 ** (power - 4)) - 0.5)
            if exp >= 10000:
                exp /= 10000
            else:
                exp /= 1000
                power -= 1
            exp = "(" + str(exp) + "x10^" + str(power) + ")"
        return "! ≈ " + figure[0] + "10^" + str(exp)


def locate_numbers(string):
    """Locates any numbers immediately followed by an exclamation mark,
    indicating that the victim has accidentally turned a number into
    its factorial.
    """
    raw_results = findall("[ /]+[\-]?.[0-9]*![?,.]*", " " + string)
    results = []
    for result in raw_results:
        prefix = ""
        result = result.strip()[:-1]
        while match("[0-9]", result) is None:
            if result[:1] != "/":
                prefix += result[:1]
            result = result[1:]
        while search("[0-9]$", result) is None:
            result = result[:-1]
        if len(result) <= length_limit:
            results.append([prefix, int(result)])
    return results


########################################################################
# Listener Functions
########################################################################

async def help(client=None, message=None, server=None, **_):
    if client is None or message is None:
        return
    msg = "I eat factorials for breakfast, lunch, and dinner. To feed me"
    msg += " one, type in a number followed by '!' an exclamation mark."
    msg += " I'll heartily digest it and give you the result!"
    msg += "\nExample: ``5!``"
    await client.send_message(message.channel, msg)


async def on_message(client=None, message=None, server=None, **_):
    nums = locate_numbers(message.content)
    if len(nums) > 0:
        # So apparently message.author.nick has a chance to be None...
        ohno = "You've uttered "
        if server is not None:
            name = message.author.nick or message.author.name
            ohno = name + " has uttered "
        ohno += "some factorials!" if len(nums) > 1 else "a factorial!"
        
        # Perform factorials, but no more than max_mentions worth.
        maxed = False
        if len(nums) > max_mentions:
            maxed = True
            nums = nums[:max_mentions]
        for figure in nums:
            ohno += "\n``" + figure[0] + str(figure[1]) \
                                        + get_factorial(figure) + "``"
        if maxed:
            ohno += "\nand others..."
        await client.send_message(message.channel, ohno)


########################################################################
# Module Functions
########################################################################

def init(module=None, **_):
    if module is None:
        return False
    module.primary = True
    module.add_listener(help, "help")
    module.add_listener(on_message, "on_message")
    module.add_name("factorial")
    module.add_name("factoral")
    module.add_name("factorals")
    return True


# Testing functions...
if __name__ == "__main__":
    test = locate_numbers("I rate it 10/10!!!")
    print(test)
    print(get_factorial(test[0]))








