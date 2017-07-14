from discord.ext import commands

from math import ceil, factorial, floor, log, pi
from nyxutils import respond
from re import findall, match, search

ram_constant = log(pi) / 2
decimal_past = 9999999999999999  # 16 9s, I guess...
estimate_past = 10000
length_limit = 100
max_mentions = 8


def get_factorial(figure):
    """/r/unexpectedfactorial"""
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
    raw_results = findall("[ ]+[0-9]*[\-]?.[0-9]*![?,.]*", " " + string)
    results = []
    for result in raw_results:
        prefix = ""
        result = result.strip()[:-1]
        divider = search("[0-9][^[0-9]]*[0-9]", result)
        if divider is not None:
            prefix = result[:divider.span()[1] - 1]
            result = result[divider.span()[1] - 1:]
        while match("[0-9]", result) is None:
            prefix += result[:1]
            result = result[1:]
        while search("[0-9]$", result) is None:
            result = result[:-1]
        if len(result) <= length_limit:
            results.append([prefix, int(result)])
    return results


async def on_message(message):
    if message.author.bot:
        return
    nums = locate_numbers(message.content)
    guild = message.guild
    if len(nums) > 0:
        oh_no = "You've uttered "
        if guild is not None:
            name = message.author.nick or message.author.name
            oh_no = name + " has uttered "
        oh_no += "some factorials!" if len(nums) > 1 else "a factorial!"
        maxed = len(nums) > max_mentions
        if maxed:
            nums = nums[:max_mentions]
        for figure in nums:
            oh_no += "".join(
                ["\n``", figure[0], str(figure[1]), get_factorial(figure),
                 "``"])
        if maxed:
            oh_no += "\nand others..."
        await message.channel.send(oh_no)


class Factorial:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    async def factorial(self, ctx, number: int):
        """I eat factorials for breakfast, lunch, and dinner. To feed me one,
        type in a number followed by '!' an exclamation mark. I'll heartily
        digest it and give you the result!
        """
        await respond(ctx, "".join([str(number), get_factorial(["", number])]))


def setup(bot):
    bot.add_cog(Factorial(bot))
    bot.add_listener(on_message)
