import time
import discord
from discord import app_commands
from discord.ext import commands

class Features(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def timestamp(self,interaction: discord.Interaction):
        try:
            seconds_since_epoch = round(time.time())
            msg = f"\\<t:{str(seconds_since_epoch)}:d>\n"
            msg += f"<t:{str(seconds_since_epoch)}:d>\n\n"
            
            msg += f"\\<t:{str(seconds_since_epoch)}:D>\n"
            msg += f"<t:{str(seconds_since_epoch)}:D>\n\n"
            
            msg += f"\\<t:{str(seconds_since_epoch)}:t>\n"
            msg += f"<t:{str(seconds_since_epoch)}:t>\n\n"
            
            msg += f"\\<t:{str(seconds_since_epoch)}:T>\n"
            msg += f"<t:{str(seconds_since_epoch)}:T>\n\n"

            msg += f"\\<t:{str(seconds_since_epoch)}:f>\n"
            msg += f"<t:{str(seconds_since_epoch)}:f>\n\n"

            msg += f"\\<t:{str(seconds_since_epoch)}:F>\n"
            msg += f"<t:{str(seconds_since_epoch)}:F>\n\n"

            msg += f"\\<t:{str(seconds_since_epoch)}:R>\n"
            msg += f"<t:{str(seconds_since_epoch)}:R>\n\n"

            msg += str(seconds_since_epoch)
            await interaction.response.send_message(msg, ephemeral=True,delete_after=60)
        except Exception as e:
            print(e,", timestamp")

async def setup(bot: commands.Bot):
    await bot.add_cog(Features(bot))