import discord
import os
import math
import json
import time

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"

CACHE_TIMEOUT = 5
json_cache = {
    "data": None,
    "timestamp": 0
}

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
            json_cache["data"] = file
            json_cache["timestamp"] = time.time()
            return util.json_read(path)
        except Exception as e:
            print(e, ", json_w")

    
    def json_read(file_path:str):
        try:
            global json_cache
            current_time = time.time()
            if json_cache["data"] is None or current_time - json_cache["timestamp"] > CACHE_TIMEOUT:
                if os.path.exists(file_path):
                    with open(file_path, 'r',encoding="utf8") as f:
                        json_cache["data"] = json.load(f)
                        json_cache["timestamp"] = current_time
                else:
                    json_cache["data"] = {}
                    json_cache["timestamp"] = current_time
            return json_cache["data"]
        except Exception as e:
            print(e,", jr")


    def player_detail(interaction:discord.Interaction,rpg_stats) -> dict:
        try:
            return rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]
        except Exception as e:
            print(e, ", player detail")
            return None
        
    def level_up(player_detail:dict)->list:#[level,experience]
        level = player_detail["level"]
        experience = player_detail["experience"]
        while experience >= util.experience_required(level):
            # Check if the player has enough experience to level up
            experience -= util.experience_required(level)  # Deduct the required experience for the next level
            level += 1  # Increment the player's level
            return [level,experience]



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
            return default_param+level*2*bouns