########################################################################
# /r/unexpectedfactorial
########################################################################
# Honestly, this was some decent practice with regex...

from math import ceil, factorial, floor, log, pi
from re import findall, match

ram_constant = log(pi) / 2
decimal_past = 9999999999
estimate_past = 10000
length_limit = 100


########################################################################
# /r/unexpectedfactorial
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
    raw_results = findall("[ ]+[\-]?.[0-9]*![ ]+", " " + string + " ")
    results = []
    for result in raw_results:
        prefix = ""
        result = result.strip()[:-1]
        while match("[0-9]", result) is None:
            prefix += result[:1]
            result = result[1:]
        if len(result) <= length_limit:
            results.append([prefix, int(result)])
    return results


########################################################################
# /r/unexpectedfactorial
########################################################################

async def on_message(client=None, message=None, server=None, **_):
    print("message")
    if client is None or message is None or server is None:
        return
    nums = locate_numbers(message.content)
    if len(nums) > 0:
        # So apparently message.author.nick has a chance to be None...
        name = message.author.nick or message.author.name
        ohno = "Suddenly, " + name + " has uttered "
        ohno += "some factorials!" if len(nums) > 1 else "a factorial!"
        for figure in nums:
            ohno += "\n``" + figure[0] + str(figure[1]) \
                                        + get_factorial(figure) + "``"
        await client.send_message(message.channel, ohno)


def init(module=None, **_):
    if module is None:
        return False
    module.primary = True
    module.add_listener(on_message, "on_message")
    return True


# Testing functions...
if __name__ == "__main__":
    print(locate_numbers("It's over 9000!"))
    test = int("9" * 100)
    print(get_factorial(["$", test]))








