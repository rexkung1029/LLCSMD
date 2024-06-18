import discord

from util import Util

j_stats_p = "Rpg/rpg_stats.json"
j_setting_p = "Rpg/rpg_setting.json"
player_detail = {}


async def status(interaction: discord.Interaction):
    try:
        player_detail = Util.Rpg.player_detail(interaction)
        player_status = player_detail.copy()
        del player_status["inventory"]
        del player_status["skills"]
        del player_status["attack_skills"]

        embed = discord.Embed(title="Player Status", color=discord.Color.green())

        for key, value in player_status.items():
            if key == "experience":
                m = Util.Rpg.experience_required(player_detail["level"])
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}({round((int(value)/m)*100)}%)", inline=False)
            
            elif key == "attack":
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "defense":
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "health":
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False) 

            elif key == "mana":
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)  

            elif key == "agility":
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "magic_resistance": 
                m = Util.Rpg.params_maximum(player_status, key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            else:
                embed.add_field(name=key.capitalize(), value=value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(e,", status")
