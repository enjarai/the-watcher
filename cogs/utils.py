import logging

import nextcord
from nextcord.ext import commands


class Utils(commands.Cog):

    def __init__(self, bot):
        self.LOGGER = logging.getLogger('utils')

        self.bot = bot

    @nextcord.slash_command(name="ping", description="Test if slash commands work properly")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("pong")

    @nextcord.slash_command(name="sus", description="Amogus")
    async def sus(self, interaction: nextcord.Interaction):
        await interaction.send(
            ':black_large_square::red_square::red_square::red_square:\n:red_square::red_square::blue_square'
            '::blue_square:\n:red_square::red_square::red_square::red_square:\n:black_large_square::red_square'
            '::red_square::red_square:\n:black_large_square::red_square::black_large_square::red_square:')


def setup(bot):
    bot.add_cog(Utils(bot))
