import discord

from rpg.util import util

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

class item():
    async def inventory(interaction:discord.Interaction):
        try:
            rpg_stats = util.json_read(j_stats_p)
            player_detail = util.player_detail(interaction,rpg_stats)
            inventory = player_detail.get("inventory", {})
            embed = discord.Embed(title="Inventory Items", color=discord.Color.blue())

            for item, quantity in inventory.items():
                embed.add_field(name=item, value=f"Quantity: {quantity}", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e,", inventory")