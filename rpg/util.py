import discord
import random
import math
import json
import numpy

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
    
    def experience_required(level):
        return math.ceil(100 * (1.1 ** level))
    
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


        elif param == "magic":
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