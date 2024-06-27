import discord

from util import util
from discord import app_commands
from discord.ext import commands

j_arangement_p = "arangement.json"

class Moderation(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
    
    def has_admin_permissions():
        def predicate(interaction: discord.Interaction):
            return interaction.user.guild_permissions.administrator
        return app_commands.check(predicate)

    @app_commands.command(name="warn")
    @has_admin_permissions()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, time: int = 1, reason:str= "No reason"):
        """
        Warns a member and optionally sets a duration for the warning.

        :param interaction: The interaction object.
        :param member: The member to warn.
        :param time: The time(s) of the warn. Default is 1 time.
        """
        try:
            gid = member.guild.id
            pid = member.id
            
            arangement = util.json_read(j_arangement_p)
            if str(gid) not in arangement["warn"]:
                arangement["warn"][str(gid)] = {}
                util.json_write(j_arangement_p,arangement)
           
            arangement = util.json_read(j_arangement_p)
            if str(pid) not in arangement["warn"][str(gid)]:
                arangement = util.json_read(j_arangement_p)
                arangement["warn"][str(gid)][str(pid)] = 0
                util.json_write(j_arangement_p,arangement)
            
            arangement = util.json_read(j_arangement_p)
            total_warn = util.moderation.get_warn(member) + time
            util.moderation.set_warn(member,time)
            dm = f"You have been warned for {time} time(s) in guild {interaction.guild.name}.Total warn {total_warn}. Reason: {reason}"
            await member.send(dm)
            await interaction.response.send_message(f"{member.mention} has been warned for {time} time(s).Total warn {total_warn}", ephemeral=True)

            await self.warn_check(member,interaction)
        except Exception as e:
            print(e, ", warn")
    
    @app_commands.command(name="check_warn")
    async def list_warn(self,interaction:discord.Interaction):
        try:
            warns = util.moderation.get_warn(interaction.user)
            await interaction.response.send_message(f"Current warn(s): {warns}")    
        except Exception as e:
            print(e,", list warn")
    

    async def warn_check(self, member: discord.Member, interaction: discord.Interaction):
            try:
                if util.moderation.get_warn(member) >= 3:
                    class BanCheck(discord.ui.View):
                        def __init__(self, member: discord.Member):
                            super().__init__()
                            self.member = member

                        @discord.ui.button(label="Sure", style=discord.ButtonStyle.danger)
                        async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
                            await self.member.ban(reason="Accumulated 3 warnings")
                            await interaction.response.send_message(f"{self.member.mention} has been banned for accumulating 3 warnings.", ephemeral=True)

                        @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
                        async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
                            await interaction.response.send_message(f"{self.member.mention} has not been banned.", ephemeral=True)

                    await interaction.followup.send(f"{member.mention} has received 3 warnings. Do you want to ban this member?", view=BanCheck(member), ephemeral=True)
            except Exception as e:
                print(e, "warn_check")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
