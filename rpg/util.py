import discord
import os
import math
import json
import time
import random

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"



with open(j_stats_p, "r", encoding="utf8") as tmp:
    rpg_stats = json.load(tmp)

with open(j_setting_p, "r", encoding="utf8") as tmp:
    rpg_setting = json.load(tmp)

class util():
    def bonus(player: dict):
        depth = player["depth"] - 1
        return 1.0 + (depth * 0.05)
    

    def experience_required(level:int):
        return math.ceil(100 * (1.1 ** level))
    

    def json_write(path: str, file):
        try:
            with open(path, 'w', encoding='utf8') as tmp:
                json.dump(file, tmp, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e, ", json_w")

    
    def json_read(file_path:str):
        try:
            with open(file_path, 'r',encoding="utf8") as f:
                data = json.load(f)
            return data 
        except Exception as e:
            print(e,", jr")


    def player_detail(interaction:discord.Interaction,rpg_stats) -> dict:
        try:
            return rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]
        except Exception as e:
            print(e, ", player detail")
            return None


    async def level_up(interaction: discord.Interaction) -> list:  # [level, experience]
        player_detail = util.player_detail(interaction, rpg_stats)
        level = player_detail["level"]
        experience = player_detail["experience"]
        if experience >= util.experience_required(level):
            while experience >= util.experience_required(level):
                # Deduct the required experience for the next level
                experience -= util.experience_required(level)
                # Increment the player's level
                level += 1
                player_detail["level"] = level
                player_detail["experience"] = experience 
                print(level)
                print(experience)
            # Return the updated level and experience
            rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = player_detail
            util.json_write(j_stats_p, rpg_stats)
            await interaction.followup.send(f"Level upped, now level: {level}",ephemeral=True)

    def generate_random_event(events: dict):
        rand = random.random()
        cumulative_probability = 0.0

        for event, probability in events.items():
            cumulative_probability += probability
            if rand < cumulative_probability:
                return event
        return None


    def params_maximum(player_detail:dict,param:str)->int:
        level = player_detail["level"]
        occupation = player_detail["occupation"]
        default_param = rpg_setting["occupation_default_params"][occupation][param]
        bouns = 1
        
        if param in ["attack","defense"]:
            if occupation =="warrior":
                bouns=1.2
            elif occupation == "archer":
                bouns=1.1
            return default_param+level*2*bouns    
        
        elif param == "health":
            if occupation =="warrior":
                bouns=1.2
            elif occupation == "archer":
                bouns=1.1
            return default_param+level*15*bouns    


        elif param == "mana":
            if occupation == "mage":
                bouns = 1.5
            elif occupation == "archer":
                bouns=1.2
            return default_param+level*5*bouns
        
        elif param == "agility":
            if occupation == "archer":
                bouns = 1.5
            elif occupation == "warrior":
                bouns = 1.2
            return default_param+level*2*bouns
        
        elif param == "magic_resistance":
            if occupation == "mage":
                bouns = 1.5
            elif occupation == "archer":
                bouns = 1.1
            return default_param+level*0.2*bouns