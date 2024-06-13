import discord
import json

from rpg.util import util

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

with open(j_stats_p, "r", encoding="utf8") as tmp:  
    rpg_stats = json.load(tmp)

with open(j_setting_p, "r", encoding="utf8") as tmp:
    rpg_setting = json.load(tmp)

class MerchantView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, player_detail: dict):
        super().__init__()
        self.interaction = interaction
        self.player_detail = player_detail

    @discord.ui.button(label="Buy Weapon (50 coins)", style=discord.ButtonStyle.primary)
    async def buy_weapon(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            rpg_stats:dict = util.json_read(j_stats_p)
            if self.player_detail["money"] >= 50:
                self.player_detail["money"] -= 50
                self.player_detail["attack"] = min(self.player_detail["attack"] * 1.1, util.params_maximum(self.player_detail, "attack"))
                rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]=self.player_detail
                util.json_write(j_stats_p, rpg_stats)
                rpg_stats = util.json_read(j_stats_p)
                await interaction.response.send_message("Your weapon has been upgraded!", ephemeral=True)
            else:
                await interaction.response.send_message("You don't have enough money to buy a weapon.", ephemeral=True)
            await self.check_continue_shopping()
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy Armor (50 coins)", style=discord.ButtonStyle.primary)
    async def buy_armor(self, interaction: discord.Interaction, button: discord.ui.Button):
        rpg_stats:dict = util.json_read(j_stats_p)
        if self.player_detail["money"] >= 50:
            self.player_detail["money"] -= 50
            self.player_detail["defense"] = min(self.player_detail["defense"] * 1.1, util.params_maximum(self.player_detail, "defense"))
            rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]=self.player_detail
            util.json_write(j_stats_p, rpg_stats)
            rpg_stats = util.json_read(j_stats_p)
            await interaction.response.send_message("Your armor has been upgraded!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough money to buy armor.", ephemeral=True)
        await self.check_continue_shopping()

    @discord.ui.button(label="Buy Health Potion (80 coins)", style=discord.ButtonStyle.primary)
    async def buy_health_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        rpg_stats:dict = util.json_read(j_stats_p)
        if self.player_detail["money"] >= 80:
            self.player_detail["money"] -= 80
            self.player_detail["inventory"]["health_potion"] = self.player_detail["inventory"].get("health_potion", 0) + 1
            rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]=self.player_detail
            util.json_write(j_stats_p, rpg_stats)
            rpg_stats = util.json_read(j_stats_p)
            await interaction.response.send_message("You bought a health potion!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough money to buy a health potion.", ephemeral=True)
        await self.check_continue_shopping()

    @discord.ui.button(label="Buy Magic Potion (100 coins)", style=discord.ButtonStyle.primary)
    async def buy_magic_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        rpg_stats:dict = util.json_read(j_stats_p)
        if self.player_detail["money"] >= 100:
            self.player_detail["money"] -= 100
            self.player_detail["inventory"]["magic_potion"] = self.player_detail["inventory"].get("magic_potion", 0) + 1
            rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]=self.player_detail
            util.json_write(j_stats_p, rpg_stats)
            rpg_stats = util.json_read(j_stats_p)
            await interaction.response.send_message("You bought a magic potion!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough money to buy a magic potion.", ephemeral=True)
        await self.check_continue_shopping()

    @discord.ui.button(label="Stop Shopping", style=discord.ButtonStyle.danger)
    async def stop_shopping(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You decided to stop shopping.", ephemeral=True)
        self.stop()

    async def check_continue_shopping(self):
        if self.player_detail["money"] < 50:
            await self.interaction.followup.send("You don't have enough money to continue shopping.", ephemeral=True)
            self.stop()
        else:
            await self.interaction.followup.send("Would you like to buy anything else?", view=self, ephemeral=True)


async def event_merchant(self, interaction: discord.Interaction):
    rpg_stats = util.json_read(j_stats_p)
    player_detail = util.player_detail(interaction,rpg_stats)
    if not player_detail:
        await interaction.followup.send("Player detail not found.", ephemeral=True)
        return

    await interaction.followup.send("Welcome to the merchant! What would you like to buy?", view=MerchantView(interaction, player_detail), ephemeral=True)
