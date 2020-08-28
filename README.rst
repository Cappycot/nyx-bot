Nyx
===

.. image:: https://img.shields.io/codeclimate/maintainability/Cappycot/nyx.svg
    :alt: Code Climate
    :target: https://codeclimate.com/github/Cappycot/nyx

An experimental extension of Rapptz's Discord bot platform that supports command name collisions - largely an unnecessary exercise.

Installation:
=============
First get Python 3.6+ with Pip and install discord.py:

``python3 -m pip install -U discord.py[voice]``

Then you can install Nyx with:

``python3 -m pip install -U git+https://github.com/Cappycot/nyx-bot``

Usage:
======
(WIP) Nyx runs the same as a Discord commands extension bot.

.. code-block:: python

    from nyxbot import NyxBot
    prefix = "$"
    token = "A token from a config file or environment variable."
    bot = NyxBot(command_prefix=prefix)
    bot.run(token)
