import discord
import random
import math
import json
import numpy

import rpg.rpg_merchant as merchant

from rpg.util import util
from discord.ext import commands, tasks
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
            "monster": self.event_monster,
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
            Choice(name="VIew Skills", value="skills")
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
                player_detail = util.player_detail(interaction,rpg_stats)
            except Exception as e:
                print(e,",rpg")

        if opt == "explore":
            try:
                await interaction.response.send_message("Start exploring", ephemeral=True)
                await self.new_event(interaction)
            except Exception as e:
                print(e,", explore")
    
        elif opt == "inventory":
            try:
                player_detail = util.player_detail(interaction,rpg_stats)
                inventory = player_detail.get("inventory", {})
                embed = discord.Embed(title="Inventory Items", color=discord.Color.blue())

                for item, quantity in inventory.items():
                    embed.add_field(name=item, value=f"Quantity: {quantity}", inline=False)

                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                print(e,", inventory")

        elif opt == "status":       
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

        elif opt == "attack_skills":
            try:
                rpg_stats = util.json_read(j_stats_p)
                player_detail = util.player_detail(interaction,rpg_stats)
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
                player_detail = util.player_detail(interaction,rpg_stats)
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
        try:
            player_detail = util.player_detail(interaction,rpg_stats)
            [player_detail["level"],player_detail["experience"]] = util.level_up(player_detail)
            util.json_write(j_stats_p,rpg_stats)
            await interaction.followup.send(f"Level upped, now level: {player_detail["level"]}",ephemeral=True)
        except Exception as e:print(e,", level up")

    # -----事件----------事件----------事件----------事件-----
    async def event_monster(self, interaction: discord.Interaction):
        monster = self.generate_random_event(self.monsters)
        rpg_stats = util.json_read(j_stats_p)
        player_detail = util.player_detail(interaction,rpg_stats)
        monster_detail = self.monsters_params[monster]
        
        class FightView(discord.ui.View):
            def __init__(self):
                super().__init__()

            @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
            async def fight_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                rpg_stats:dict = util.json_read(j_stats_p)
                try:
                    damage_status = rpg_main.fight(rpg_main, player_detail, monster_detail)
                    if damage_status[1] <= 0:
                        player_detail["health"] = damage_status[0]
                        exp_gain = monster_detail["experience"] * util.bonus(player_detail)
                        money_gain = exp_gain * 2
                        player_detail["experience"] += exp_gain
                        player_detail["money"] += money_gain
                        await interaction.response.send_message(f"You defeated {monster}, gaining {exp_gain} experience points and {money_gain} copper coins!", ephemeral=True)
                        util.json_write(j_stats_p, rpg_stats)
                        rpg_stats = util.json_read(j_stats_p)
                    elif damage_status[0] <= 0:                        
                        player_detail["money"] = max(0, player_detail["money"] - 20)
                        await interaction.response.send_message("You died haha. Use `/rpg explore` to continue your adventure. \nDeducted 20 copper coins", ephemeral=True)
                except Exception as e:
                    print(e, " ,fight button")

            @discord.ui.button(label="Run", style=discord.ButtonStyle.secondary)
            async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message("You successfully escaped!", ephemeral=True)


        await interaction.followup.send(f"You encountered {monster}, do you want to fight?", view=FightView(), ephemeral=True)


    async def event_treasure_chest(self, interaction: discord.Interaction):
        try:
            rpg_stats:dict = util.json_read(j_stats_p)
            content = self.generate_random_event(self.treasure_contents)
            player_detail = util.player_detail(interaction,rpg_stats)
            player_detail["experience"] += 50
            if content == "health_potion":
                heal = round(numpy.random.normal(25,5))
                if heal < 1: heal = 1
                elif heal > 50: heal = 50
                heal = round(heal * util.bonus(player_detail))
                player_detail["health"] = min(player_detail["health"] + heal, util.params_maximum(player_detail,"health"))
                await interaction.followup.send(f"You obtained a Health Potion, restoring {heal} health points!", ephemeral=True)
            
            elif content == "weapon":
                player_detail["attack"] = min(player_detail["attack"] * 1.1, util.params_maximum(player_detail,"attack"))
                await interaction.followup.send("Your weapon has been upgraded!", ephemeral=True)
            
            elif content == "armor":
                player_detail["defense"] = min (player_detail["defense"] * 1.1, util.params_maximum(player_detail,"defense"))
                await interaction.followup.send("Your armor has been upgraded!", ephemeral=True)
            
            elif content == "money":
                money = round(numpy.random.normal(50,20))
                money = round(money * util.bonus(player_detail))
                player_detail["money"] += money
                await interaction.followup.send(f"You obtained {money} copper coins!", ephemeral=True)
            
            util.json_write(j_stats_p, rpg_stats)
            rpg_stats = util.json_read(j_stats_p)
        except Exception as e:
            print(e, ", chest")



    async def event_special_room(self, interaction: discord.Interaction):
        room = self.generate_random_event(self.special_rooms)
        if room == "merchant":
            await merchant.event_merchant(self=merchant,interaction=interaction)
        if room == "coach":
            pass


    async def event_stairs(self, interaction: discord.Interaction):
        try:
            player_detail = util.player_detail(interaction,rpg_stats)
            
            class FloorDecisionView(discord.ui.View):
                def __init__(self, interaction: discord.Interaction):
                    super().__init__()

                @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
                async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    player_detail["depth"] += 1
                    player_detail["money"] += 100
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


    def generate_random_event(self, events: dict):
        rand = random.random()
        cumulative_probability = 0.0

        for event, probability in events.items():
            cumulative_probability += probability
            if rand < cumulative_probability:
                return event
        return None

    async def new_event(self, interaction: discord.Interaction):
        event = self.generate_random_event(self.events)
        if event:
            event_message = self.events_msg[event]
            await interaction.followup.send(f"{event_message}", ephemeral=True)
            await self.execute_event(event_name=event, interaction=interaction)
        else:
            await interaction.followup.send("No event occurred.", ephemeral=True)


    # -----戰鬥----------戰鬥----------戰鬥----------戰鬥-----

    def fight(self, player: dict, monster: dict) -> list:  # [player left hp, monster left hp]
        try:
            player_hp, monster_hp = player["health"], monster["health"] * util.bonus(player)
            player_attack = player["attack"]
            monster_attack = monster["attack"]
            player_defend = player["defense"]
            monster_defend = monster["defense"]

            while True:
                # Calculate damage to monster
                player_damage = max(0, (player_attack / monster_defend) % 1)
                monster_hp -= round(max(player_damage, player_attack - monster_defend))
                if monster_hp <= 0:
                    monster_hp = 0
                    break

                # Calculate damage to player
                monster_damage = max(0, (monster_attack / player_defend) % 1)
                player_hp -= round(max(monster_damage, monster_attack - player_defend))
                if player_hp <= 0:
                    player_hp = 0
                    break

            return [player_hp, monster_hp]
        except Exception as e:
            print(e,", fight")

async def setup(bot: commands.Bot):
    await bot.add_cog(rpg_main(bot))
