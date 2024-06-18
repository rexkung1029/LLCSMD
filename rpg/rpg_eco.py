from discord.ext import commands


class Money(commands.Cog):
    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Money(bot))
