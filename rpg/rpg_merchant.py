import discord
import json

from util import util

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

class MerchantView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, player_detail: dict):
        super().__init__()
        self.interaction = interaction
        self.player_detail = player_detail

    @discord.ui.button(label="Buy Weapon (50 coins)", style=discord.ButtonStyle.primary)
    async def buy_weapon(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.player_detail["money"] >= 50:
                self.player_detail["money"] -= 50
                self.player_detail["inventory"]["weapon_upgrade"] = self.player_detail["inventory"].get("weapon_upgrade", 0) + 1
                util.rpg.player_detail_update(interaction,self.player_detail)
                await interaction.response.send_message("You bought a weapon upgrade!", ephemeral=True)
            else:
                await interaction.response.send_message("You don't have enough money to buy a weapon upgrade.", ephemeral=True)
            await self.check_continue_shopping()
        except Exception as e:
            print(e)

    @discord.ui.button(label="Buy Armor (50 coins)", style=discord.ButtonStyle.primary)
    async def buy_armor(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player_detail["money"] >= 50:
            self.player_detail["money"] -= 50
            self.player_detail["inventory"]["armor_upgrade"] = self.player_detail["inventory"].get("armor_upgrade", 0) + 1
            util.rpg.player_detail_update(interaction,self.player_detail)
            await interaction.response.send_message("You bought an armor upgrade!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough money to buy armor upgrade.", ephemeral=True)
        await self.check_continue_shopping()

    @discord.ui.button(label="Buy Health Potion (80 coins)", style=discord.ButtonStyle.primary)
    async def buy_health_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player_detail["money"] >= 80:
            self.player_detail["money"] -= 80
            self.player_detail["inventory"]["health_potion"] = self.player_detail["inventory"].get("health_potion", 0) + 1
            util.rpg.player_detail_update(interaction,self.player_detail)
            await interaction.response.send_message("You bought a health potion!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough money to buy a health potion.", ephemeral=True)
        await self.check_continue_shopping()

    @discord.ui.button(label="Buy Magic Potion (100 coins)", style=discord.ButtonStyle.primary)
    async def buy_magic_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player_detail["money"] >= 100:
            self.player_detail["money"] -= 100
            self.player_detail["inventory"]["magic_potion"] = self.player_detail["inventory"].get("magic_potion", 0) + 1
            util.rpg.player_detail_update(interaction,self.player_detail)
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


async def event_merchant(interaction: discord.Interaction):
    player_detail = util.rpg.player_detail(interaction)
    if not player_detail:
        await interaction.followup.send("Player detail not found.", ephemeral=True)
        return

    await interaction.followup.send(f"Welcome to the merchant! What would you like to buy?\nYou now have {player_detail["money"]} copper coin", 
                                    view=MerchantView(interaction, player_detail), ephemeral=True)