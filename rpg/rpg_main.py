import discord
import random
import math
import json
import numpy

import rpg.rpg_merchant as merchant

from rpg.util import util
from rpg.rpg_fight import fight
from rpg.rpg_item import item
import rpg.rpg_status as status

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

j_stats_p = "rpg/rpg_stats.json"    
j_setting_p = "rpg/rpg_setting.json"

rpg_stats = {}
rpg_setting={}

with open(j_stats_p, "r", encoding="utf8") as tmp:
    rpg_stats:dict = json.load(tmp)

with open(j_setting_p, "r", encoding="utf8") as tmp:
    rpg_setting = json.load(tmp)


class rpg_main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = rpg_setting["events"]
        self.monsters = rpg_setting["monsters"]
        self.events_msg = rpg_setting["events_msg"]
        self.monsters_params = rpg_setting["monsters_params"]
        self.treasure_contents = rpg_setting["treasure_contents"]
        self.special_rooms = rpg_setting["special_rooms"]
        self.event_functions = {
            "treasure chest": self.event_treasure_chest,
            "special_room": self.event_special_room,
            "stairs": self.event_stairs
        }


    @app_commands.command(name="rpg")
    @app_commands.choices(
        opt=[
            Choice(name="Start", value="start"),
            Choice(name="Explore", value="explore"),
            Choice(name="View Inventory", value="inventory"),
            Choice(name="View Status",value="status"),
            Choice(name="VIew Attack Skills", value="attack_skills"),
            Choice(name="VIew Skills", value="skills"),
            Choice(name="Use item", value="use")
        ]
    )
    async def rpg(self, interaction: discord.Interaction, opt: str = "explore"):
        rpg_stats:dict = util.json_read(j_stats_p)
        print(opt)
        try:
            if str(interaction.guild_id) not in rpg_stats:
                rpg_stats[str(interaction.guild_id)] = {}
                util.json_write(j_stats_p, rpg_stats)
            rpg_stats = util.json_read(j_stats_p)
        except Exception as e:
            print(e,", setup")
        
        if opt == "start":
            try:
                if str(interaction.user.id) not in rpg_stats[str(interaction.guild_id)]:
                    class OccupationSelectionView(discord.ui.View):
                        @discord.ui.button(label="Warrior", style=discord.ButtonStyle.primary)
                        async def select_warrior(self, interaction: discord.Interaction, button: discord.ui.Button):
                            self.create_character(interaction,"warrior")
                            await interaction.response.send_message("Warrior character created successfully", ephemeral=True)

                        @discord.ui.button(label="Mage", style=discord.ButtonStyle.primary)
                        async def select_mage(self, interaction: discord.Interaction, button: discord.ui.Button):
                            self.create_character(interaction,"mage")
                            await interaction.response.send_message("Mage character created successfully", ephemeral=True)

                        @discord.ui.button(label="Archer", style=discord.ButtonStyle.primary)
                        async def select_archer(self, interaction: discord.Interaction, button: discord.ui.Button):
                            self.create_character(interaction, "archer")
                            await interaction.response.send_message("Archer character created successfully", ephemeral=True)
                        
                        def create_character(self, interaction:discord.Interaction, occupation:str):
                            guild_id = str(interaction.guild_id)
                            user_id = str(interaction.user.id)
                            self.occupation_default_params = rpg_setting["occupation_default_params"]
                            
                            rpg_stats:dict = util.json_read(j_stats_p)
                            rpg_stats.setdefault(guild_id, {})
                            rpg_stats[guild_id][user_id] = {
                                "name": interaction.user.nick or interaction.user.name,
                                "occupation": occupation,
                                **self.occupation_default_params["common"],
                                **self.occupation_default_params[occupation]
                            }

                            util.json_write(j_stats_p, rpg_stats)
                            rpg_stats = util.json_read(j_stats_p)
                    await interaction.response.send_message("Please choose an occupation:", view=OccupationSelectionView(), ephemeral=True)
                else:
                    await interaction.response.send_message("You already have a character", ephemeral=True)
            except Exception as e:
                print(e,", start")

        else:
            try:
                if str(interaction.user.id) not in rpg_stats[str(interaction.guild_id)]:
                    await interaction.response.send_message("You don't have a character.")
                    return
                player_detail = util.player_detail(interaction)
            except Exception as e:
                print(e,",rpg")

        if opt == "explore":
            try:
                await interaction.response.send_message("Start exploring", ephemeral=True)
                await self.new_event(interaction)
            except Exception as e:
                print(e,", explore")
    
        elif opt == "inventory":
            await item.inventory(interaction)

        elif opt == "status":       
            await status.status(interaction)

        elif opt == "attack_skills":
            try:
                rpg_stats = util.json_read(j_stats_p)
                player_detail = util.player_detail(interaction)
                attack_skills = player_detail["attack_skills"]
                embed = discord.Embed(title="Player Attack Skills", color=discord.Color.blue())
                if attack_skills is None:
                    interaction.response.send_message("You do not have any attack skills.")
                else:
                    for name, level in attack_skills:
                        embed.add_field(name=name,value=level,inline=False)
                    await interaction.response.send_message(embed=embed,ephemeral=True)
            except Exception as e:
                print(e,", attack skills")

        elif opt == "skills":
            try:
                player_detail = util.player_detail(interaction)
                skills = player_detail["skills"]
                embed = discord.Embed(title="Player Skills", color=discord.Color.blue())
                if skills is None:
                    interaction.response.send_message("You do not have any skills.")
                else:
                    for name, level in skills:
                        embed.add_field(name=name,value=level,inline=False)
                    await interaction.response.send_message(embed=embed,ephemeral=True)
            except Exception as e:
                print(e,", skills")
        
        elif opt == "use":
            await item.use_item(item,interaction)

        await util.level_up(interaction)        

    async def event_treasure_chest(self, interaction: discord.Interaction):
        try:
            rpg_stats:dict = util.json_read(j_stats_p)
            content = util.generate_random_event(self.treasure_contents)
            player_detail = util.player_detail(interaction)
            player_detail["experience"] += 50
            if content == "health_potion":
                player_detail["inventory"]["health_potion"] = player_detail["inventory"].get("health_potion", 0) + 1
                await interaction.followup.send(f"You obtained a Health Potion!", ephemeral=True)
            
            elif content == "weapon":
                player_detail["inventory"]["weapon_upgrade"] = player_detail["inventory"].get("weapon_upgrade", 0) + 1
                await interaction.followup.send("You obtained a weapon upgrade!", ephemeral=True)
            
            elif content == "armor":
                player_detail["inventory"]["armor_upgrade"] = player_detail["inventory"].get("armor_upgrade", 0) + 1
                await interaction.followup.send("You obtained an armor upgrade !", ephemeral=True)
            
            elif content == "money":
                money = round(numpy.random.normal(50,20))
                money = round(money * util.bonus(player_detail))
                player_detail["money"] += money
                await interaction.followup.send(f"You obtained {money} copper coins!", ephemeral=True)
            
            util.player_detail_update(interaction,player_detail)
            rpg_stats = util.json_read(j_stats_p)
        except Exception as e:
            print(e, ", chest")



    async def event_special_room(self, interaction: discord.Interaction):
        room = util.generate_random_event(self.special_rooms)
        if room == "merchant":
            await merchant.event_merchant(interaction=interaction)
        if room == "coach":
            pass


    async def event_stairs(self, interaction: discord.Interaction):
        try:
            player_detail = util.player_detail(interaction)
            
            class FloorDecisionView(discord.ui.View):
                def __init__(self, interaction: discord.Interaction):
                    super().__init__()

                @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
                async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    player_detail["depth"] += 1
                    player_detail["money"] += 100
                    util.player_detail_update(interaction,player_detail)
                    await interaction.response.send_message("You chose to go downstairs.", ephemeral=True)

                @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
                async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_message("You chose not to go downstairs.", ephemeral=True)
            
            await interaction.followup.send("Do you want to go downstairs?", view=FloorDecisionView(interaction), ephemeral=True)
        except Exception as e:
            print(e, ", stair")


    async def execute_event(self, event_name, interaction: discord.Interaction):
        if event_name in self.event_functions:
            await self.event_functions[event_name](interaction)
        else:
            return "Unknown event"


    async def new_event(self, interaction: discord.Interaction):
        event = util.generate_random_event(self.events)
        if event:
            if event == "monster":
                await fight.event_monster(self=fight,interaction=interaction)
            else:
                event_message = self.events_msg[event]
                await interaction.followup.send(f"{event_message}", ephemeral=True)
                await self.execute_event(event_name=event, interaction=interaction)
        else:
            await interaction.followup.send("No event occurred.", ephemeral=True)


    # -----戰鬥----------戰鬥----------戰鬥----------戰鬥-----



async def setup(bot: commands.Bot):
    await bot.add_cog(rpg_main(bot))
