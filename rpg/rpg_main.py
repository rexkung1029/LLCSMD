import discord
import random
import math
import json
import numpy

from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"
exploring = []

with open(j_stats_p, "r", encoding="utf8") as tmp:
    rpg_stats = json.load(tmp)

with open(j_setting_p, "r", encoding="utf8") as tmp:
    rpg_setting = json.load(tmp)

class common():

    @staticmethod
    def json_write(path: str, file):
        try:
            with open(path, 'w', encoding='utf8') as tmp:
                json.dump(file, tmp, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e, ", json_w")


    @staticmethod
    def player_detail(interaction: discord.Interaction) -> dict:
        pd = rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]
        return pd


    @staticmethod
    def bonus(player: dict):
        depth = player["depth"] - 1
        return 1.0 + (depth * 0.05)
    
    @staticmethod
    def experience_required(level):
        return math.ceil(100 * (1.1 ** level))


class rpg_main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = rpg_setting["events"]
        self.monsters = rpg_setting["monsters"]
        self.events_msg = rpg_setting["events_msg"]
        self.monsters_params = rpg_setting["monsters_params"]
        self.treasure_contents = rpg_setting["treasure_contents"]
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
            Choice(name="View Status",value="status")
        ]
    )
    async def rpg(self, interaction: discord.Interaction, opt: str = "explore"):
        try:
            player_detail = common.player_detail(interaction)
            if opt == "start":
                if str(interaction.guild_id) not in rpg_stats:
                    rpg_stats[str(interaction.guild_id)] = {}
                    common.json_write(j_stats_p, rpg_stats)

                if str(interaction.user.id) not in rpg_stats[str(interaction.guild_id)]:
                    rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = {
                        "name": interaction.user.nick or interaction.user.name,
                        "level": 1,
                        "inventory": {},
                        "skills": {},
                        "experience": 0,
                        "attack": 10,
                        "health": 100,
                        "defense": 10,
                        "depth": 1,
                        "money": 50
                    }
                    common.json_write(j_stats_p, rpg_stats)
                    await interaction.response.send_message("Character created successfully", ephemeral=True)
                else:
                    await interaction.response.send_message("You already have a character", ephemeral=True)

            elif opt == "explore":
                if interaction.user.id not in exploring:
                    await interaction.response.send_message("Start exploring", ephemeral=True)
                else:
                    await interaction.response.send_message("Continue exploring", ephemeral=True)
                await self.new_event(interaction)
        
            elif opt == "inventory":
                inventory = player_detail.get("inventory", {})
                embed = discord.Embed(title="Inventory Items", color=discord.Color.blue())

                for item, quantity in inventory.items():
                    embed.add_field(name=item, value=f"Quantity: {quantity}", inline=False)

                await interaction.response.send_message(embed=embed, ephemeral=True)

            elif opt == "status":        
                player_status = player_detail.copy()
                del player_status["inventory"]
                del player_status["skills"]

                embed = discord.Embed(title="Player Status", color=discord.Color.green())

                for key, value in player_status.items():
                    embed.add_field(name=key.capitalize(), value=value, inline=False)

                await interaction.response.send_message(embed=embed, ephemeral=True)

            while player_detail["experience"] >= common.experience_required(player_detail["level"]):
                # Check if the player has enough experience to level up
                player_detail["experience"] -= common.experience_required(player_detail["level"])  # Deduct the required experience for the next level
                player_detail["level"] += 1  # Increment the player's level
                common.json_write(j_stats_p, rpg_stats)  # Update player data in the JSON file
                await interaction.followup.send(f"Congratulations! You have reached level {player_detail['level']}!")  # Notify the player of level up


        except Exception as e:
            print(e, ", rpg")


    # -----事件----------事件----------事件----------事件-----
    async def event_monster(self, interaction: discord.Interaction):
        monster = self.generate_random_event(self.monsters)
        player_detail = common.player_detail(interaction)
        monster_detail = self.monsters_params[monster]
        
        class FightView(discord.ui.View):
            def __init__(self):
                super().__init__()

            @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
            async def fight_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    damage_status = rpg_main.fight(rpg_main, player_detail, monster_detail)
                    if damage_status[1] <= 0:
                        player_detail["heealth"] = damage_status[0]
                        exp_gain = monster_detail["experience"] * common.bonus(player_detail)
                        money_gain = exp_gain * 2
                        player_detail["experience"] += exp_gain
                        player_detail["money"] += money_gain
                        await interaction.response.send_message(f"You defeated {monster}, gaining {exp_gain} experience points and {money_gain} copper coins!", ephemeral=True)
                        common.json_write(j_stats_p, rpg_stats)
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
            content = self.generate_random_event(self.treasure_contents)
            player_detail = common.player_detail(interaction)
            if content == "Health Potion":
                heal = round(numpy.random.normal(25,5))
                if heal < 1: heal = 1
                elif heal > 50: heal = 50
                heal = round(heal * common.bonus(player_detail))
                player_detail["health"] = min(player_detail["health"] + heal, 100 + player_detail["level"] * 15)
                await interaction.followup.send(f"You obtained a Health Potion, restoring {heal} health points!", ephemeral=True)
            
            elif content == "Weapon":
                player_detail["attack"] = min(player_detail["attack"] * 1.1, 10 + player_detail["level"] * 2)
                await interaction.followup.send("Your weapon has been upgraded!", ephemeral=True)
            
            elif content == "Armor":
                player_detail["defense"] = min (player_detail["defense"] * 1.1, 10 + player_detail["level"] * 2)
                await interaction.followup.send("Your armor has been upgraded!", ephemeral=True)
            
            elif content == "Money":
                money = round(numpy.random.normal(50,20))
                money = round(money * common.bonus(player_detail))
                player_detail["money"] += money
                await interaction.followup.send(f"You obtained {money} copper coins!", ephemeral=True)
            
            common.json_write(j_stats_p, rpg_stats)
        except Exception as e:
            print(e, ", chest")



    async def event_special_room(self, interaction: discord.Interaction):
        await interaction.followup.send("Special room is still under development.", ephemeral=True)


    async def event_stairs(self, interaction: discord.Interaction):
        try:
            player_detail = common.player_detail(interaction)
            
            class FloorDecisionView(discord.ui.View):
                def __init__(self, interaction: discord.Interaction):
                    super().__init__()

                @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
                async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    player_detail["depth"] += 1
                    player_detail["money"] += 10
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
            player_hp, monster_hp = player["health"], monster["health"] * common.bonus(player)
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
