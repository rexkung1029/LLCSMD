import discord
import json

from util import util

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

class item():
    async def inventory(interaction:discord.Interaction):
        try:
            player_detail: dict = util.rpg.player_detail(interaction)
            inventory:dict = player_detail.get("inventory", {})
            embed = discord.Embed(title="Inventory Items", color=discord.Color.blue())

            index = 0
            for item, quantity in inventory.items():
                index += 1
                embed.add_field(name=f"{index}.{item}", value=f"Quantity: {quantity}", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e,", inventory")

    async def use_item(self, interaction: discord.Interaction):
        try:
            inventory = util.rpg.get_inventory(interaction)
            if inventory:
                select_view = ItemUsing(interaction, inventory)
                await interaction.response.send_message("Select an item to use:", view=select_view, ephemeral=True)
            else:
                await interaction.followup.send("Your inventory is empty.", ephemeral=True)
        except Exception as e:
            print(e, ", use item")


class ItemSelect(discord.ui.Select):
    def __init__(self, inventory):
        options = [
            discord.SelectOption(label=f"{item} (x{quantity})", value=item)
            for item, quantity in inventory.items()
        ]
        super().__init__(placeholder="Choose an item to use", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_item = self.values[0]
        await interaction.response.send_message(f"You selected {self.values[0]}. Confirm to use it.", ephemeral=True)

class ItemUsing(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, inventory: dict):
        super().__init__()
        self.interaction = interaction
        self.selected_item = None

        # Add the Select menu to the view
        self.add_item(ItemSelect(inventory))

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.selected_item:
                # Logic to use the selected item
                await interaction.response.send_message(f"Using {self.selected_item}.", ephemeral=True)
                # Update the inventory after using the item
                inventory = util.rpg.get_inventory(interaction)
                util.rpg.item_use.use(interaction,self.selected_item)
                inventory[self.selected_item] -= 1
                if inventory[self.selected_item] <= 0:
                    del inventory[self.selected_item]
                util.rpg.inventory_update(interaction, inventory)  # Assuming you have a function to update the inventory
            else:
                await interaction.response.send_message("No item selected.", ephemeral=True)
        except Exception as e:
            print(e,", confirm button")

