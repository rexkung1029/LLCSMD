import discord
import numpy
import random
import json

from rpg.util import util

j_stats_p = "rpg/rpg_stats.json"    
j_setting_p = "rpg/rpg_setting.json"

rpg_setting = {}
rpg_stats={}

with open(j_setting_p, "r", encoding="utf8") as tmp:
    rpg_setting = json.load(tmp)

with open(j_stats_p, "r", encoding="utf8") as tmp:
    rpg_stats = json.load(tmp)

class fight():
    def __init__(self):
        pass

    def battle(self, player: dict, monster: dict) -> list:  # [player left hp, monster left hp]
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


    async def event_monster(self, interaction: discord.Interaction):
        print("1")
        monster = util.generate_random_event(rpg_setting["monsters"])

        await interaction.followup.send(f"You encountered {monster}, do you want to fight?", view=FightView(interaction=interaction, monster=monster), ephemeral=True)

class FightView(discord.ui.View):
    def __init__(self,interaction:discord.Interaction, monster:str):
        super().__init__()
        self.monster_detail = rpg_setting["monsters_params"][monster.capitalize()]
        self.monster = monster

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
    async def fight_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        rpg_stats:dict = util.json_read(j_stats_p)
        player_detail = util.player_detail(interaction,rpg_stats)
        try:
            damage_status = fight.battle(fight, player_detail, self.monster_detail)
            print(damage_status)
            if damage_status[1] <= 0:
                player_detail["health"] = damage_status[0]
                exp_gain = self.monster_detail["experience"] * util.bonus(player_detail)
                money_gain = exp_gain * 2
                player_detail["experience"] += exp_gain
                player_detail["money"] += money_gain
                rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = player_detail
                await interaction.response.send_message(f"You defeated {self.monster}, gaining {exp_gain} experience points and {money_gain} copper coins!", ephemeral=True)
                util.json_write(j_stats_p, rpg_stats)
                rpg_stats = util.json_read(j_stats_p)
            
            elif damage_status[0] <= 0:                        
                player_detail["money"] = max(0, player_detail["money"] - 20)
                rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = player_detail
                util.json_write(j_stats_p, rpg_stats)
                await interaction.response.send_message("You died haha. Use `/rpg explore` to continue your adventure. \nDeducted 20 copper coins", ephemeral=True)
        except Exception as e:
            print(e, " ,fight button")

    @discord.ui.button(label="Run", style=discord.ButtonStyle.secondary)
    async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        rpg_stats:dict = util.json_read(j_stats_p)
        player_detail = util.player_detail(interaction,rpg_stats)
        try:
            monster_agility = self.monster_detail["agility"]
            print(monster_agility)
            player_agility = player_detail["agility"]
            print(player_agility)
            if player_agility > 2 * monster_agility or monster_agility <= 0:
                await interaction.response.send_message("You successfully escaped!", ephemeral=True)
            elif monster_agility > 2 * player_agility or player_agility <= 0:
                fight.battle(fight,player_detail,self.monster_detail)
            else:
                prob_of_battle = abs(player_agility-monster_agility) * 2 /max(player_agility,monster_agility)
                tmp = random.random()
                if prob_of_battle > tmp and monster_agility > player_agility:
                    fight.battle(fight,player_detail,self.monster_detail)
                else:
                    await interaction.response.send_message("You successfully escaped!", ephemeral=True)
        except Exception as e:
            print(e,", run")