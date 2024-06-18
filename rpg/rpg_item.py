import discord

from util import Util

j_stats_p = "Rpg/rpg_stats.json"
j_setting_p = "Rpg/rpg_setting.json"


class Item:
    async def inventory(interaction:discord.Interaction):
        try:
            player_detail: dict = Util.Rpg.player_detail(interaction)
            inventory:dict = player_detail.get("inventory", {})
            embed = discord.Embed(title="Inventory Items", color=discord.Color.blue())

            index = 0
            for item, quantity in inventory.items():
                index += 1
                embed.add_field(name=f"{index}.{item}", value=f"Quantity: {quantity}", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e,", inventory")

    @staticmethod
    async def use_item(self, interaction: discord.Interaction):
        try:
            inventory = Util.Rpg.get_inventory(interaction)
            if inventory:
                select_view = ItemUsing(interaction, inventory)
                await interaction.response.send_message("Select an Item to use:", view=select_view, ephemeral=True)
            else:
                await interaction.followup.send("Your inventory is empty.", ephemeral=True)
        except Exception as e:
            print(e, ", use Item")


class ItemSelect(discord.ui.Select):
    def __init__(self, inventory):
        options = [
            discord.SelectOption(label=f"{item} (x{quantity})", value=item)
            for item, quantity in inventory.items()
        ]
        super().__init__(placeholder="Choose an Item to use", options=options)

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
                # Logic to use the selected Item
                await interaction.response.send_message(f"Using {self.selected_item}.", ephemeral=True)
                # Update the inventory after using the Item
                inventory = Util.Rpg.get_inventory(interaction)
                Util.Rpg.ItemUse.use(interaction, self.selected_item)
                inventory[self.selected_item] -= 1
                if inventory[self.selected_item] <= 0:
                    del inventory[self.selected_item]
                Util.Rpg.inventory_update(interaction, inventory)  # Assuming you have a function to update the inventory
            else:
                await interaction.response.send_message("No Item selected.", ephemeral=True)
        except Exception as e:
            print(e,", confirm button")
