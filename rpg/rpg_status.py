import discord

from rpg.util import util

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

async def status(interaction: discord.Interaction):
    try:
        rpg_stats = util.json_read(j_stats_p)
        player_detail = util.player_detail(interaction,rpg_stats)
        player_status = player_detail.copy()
        del player_status["inventory"]
        del player_status["skills"]
        del player_status["attack_skills"]

        embed = discord.Embed(title="Player Status", color=discord.Color.green())

        for key, value in player_status.items():
            if key == "experience":
                m = util.experience_required(player_detail["level"])
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}({round((int(value)/m)*100)}%)", inline=False)
            
            elif key == "attack":
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "defense" :
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "health":
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False) 

            elif key == "mana":
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)  

            elif key == "agility":
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            elif key == "magic_resistance": 
                m = util.params_maximum(player_status,key)
                embed.add_field(name=key.capitalize(), value=f"{value}/{m}", inline=False)

            else:
                embed.add_field(name=key.capitalize(), value=value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(e,", status")