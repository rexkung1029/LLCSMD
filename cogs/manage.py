import discord

from util import util
from discord import app_commands
from discord.ext import commands

class manage():
    def __init__(self,bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(manage(bot))
