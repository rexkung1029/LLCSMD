import discord
import os
import math
import json
import time
import random

j_stats_p = "rpg/rpg_stats.json"
j_setting_p = "rpg/rpg_setting.json"





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


    def player_detail(interaction:discord.Interaction) -> dict:
        try:
            rpg_stats = util.json_read(j_stats_p)
            return rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]
        except Exception as e:
            print(e, ", player detail")
            return None
        

    def monster_detail(monster) -> dict:
        try:
            rpg_setting = util.json_read(j_setting_p)
            return rpg_setting["monsters_params"][monster]
        except Exception as e:
            print(e, ", player detail")
            return None


    async def level_up(interaction: discord.Interaction) -> list:  # [level, experience]
        rpg_stats = util.json_read(j_stats_p)
        player_detail = util.player_detail(interaction)
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
        rpg_setting = util.json_read(j_setting_p)
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


    def get_inventory(interaction:discord.Interaction)->dict:
        return util.player_detail(interaction)["inventory"]
    
    def inventory_update(interaction:discord.Interaction,inventory:dict):
        rpg_stats = util.json_read(j_stats_p)
        rpg_stats[str(interaction.guild_id)][str(interaction.user.id)]["inventory"] = inventory
        util.json_write(j_stats_p,rpg_stats)
        return

    def player_detail_update(interaction:discord.Interaction,player_detail:dict):
        rpg_stats = util.json_read(j_stats_p)
        rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = player_detail
        util.json_write(j_stats_p,rpg_stats)
        return

    class item_use():
        def use(interaction: discord.Interaction,item:str):
            if item == "weapon_upgrade" : util.item_use.weapon(interaction)
            if item == "armor_upgrade": util.item_use.armor(interaction)
            if item == "health_potion": util.item_use.health_potion(interaction)
            if item == "mana_potion": util.item_use.mana_potion(interaction)


        def weapon(interaction):
            player_detail = util.player_detail(interaction)
            player_detail["attack"] += 3 * util.bonus(player_detail)
            util.player_detail_update(interaction,player_detail)
            return

        def armor(interaction):
            player_detail = util.player_detail(interaction)
            player_detail["defense"] += 3 * util.bonus(player_detail)
            util.player_detail_update(interaction,player_detail)
            return

        def health_potion(interaction):
            player_detail = util.player_detail(interaction)
            player_detail["health"] += 30 * util.bonus(player_detail)
            util.player_detail_update(interaction,player_detail)
            return

        def mana_potion(interaction):
            player_detail = util.player_detail(interaction)
            player_detail["mana"] += 30 * util.bonus(player_detail)
            util.player_detail_update(interaction,player_detail)
            return
        
    class fight():
        def phsycal_damage_caculate(attack:float,defense:float) -> float:
            return max(math.log(attack,defense),attack-defense)
        
    class skill():
        def attack_skill_params(detail:dict,attack_skill:dict):
            """
            [detail,round]
            """
            skill_params:dict = util.json_read(j_setting_p)["attack_skills"]
            round = attack_skill.get(["round"],1)
            del attack_skill["round"]
            for name, para in attack_skill:
                if name in skill_params["multiplier"]:
                    detail[name] *= para
                
                elif name in skill_params["increment"]:
                    detail[name] += para

                elif name in skill_params["deduct"]:
                    detail[name] -= para
                
                else :
                    print("unknown skill")
                    print(name)

            return [detail,round]
