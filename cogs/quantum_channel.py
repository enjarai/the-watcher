import asyncio
import random

from nextcord.ext import commands
from nextcord.ext import tasks


class Litematics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.CONFIG = bot.CONFIG["quantum_channel"]
        self.channels = []
        for chan in self.CONFIG["channels"]:
            self.channels.append(self.bot.get_channel(chan))
        self.quantum_loop.start()

    @tasks.loop(seconds=10)
    async def quantum_loop(self):
        for chan in self.channels:
            print("moving " + chan.name)
            max_pos = chan.category.text_channels[-1].position
            await chan.edit(position=random.randint(0, max_pos))
            await asyncio.sleep(1)


def setup(bot):
    bot.add_cog(Litematics(bot))
