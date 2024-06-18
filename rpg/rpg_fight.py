import discord
import math
import random
import json

from util import util

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

    async def battle(self, interaction:discord.Interaction, monster: str) -> bool:  # [player left hp, monster left hp]
        try:
            player_detail = util.rpg.player_detail(interaction)
            monster_detail = util.rpg.monster_detail(monster)
            player_hp, monster_hp = player_detail["health"], monster_detail["health"] * util.rpg.bonus(player_detail)
            player_attack = player_detail["attack"]
            monster_attack = monster_detail["attack"] * util.rpg.bonus(player_detail)
            player_defend = player_detail["defense"]
            monster_defend = monster_detail["defense"] * util.rpg.bonus(player_detail)
            monster_experience = monster_detail["experience"]  * util.rpg.bonus(player_detail)

            while True:
                # Calculate damage to monster
                monster_hp -= util.rpg.fight.phsycal_damage_caculate(player_attack,monster_defend)
                if monster_hp <= 0:
                    if_player_win = True
                    break

                # Calculate damage to player
                player_hp -= util.rpg.fight.phsycal_damage_caculate(monster_attack,player_defend)
                if player_hp <= 0:
                    if_player_win = False
                    break

            if if_player_win:
                await interaction.response.send_message(f"You defeated {monster}, gaining {monster_experience} experience points and {2 * monster_experience} copper coins!")
            
            else :
                await interaction.response.send_message(
                    "You died haha. Use /rpg explore to continue your adventure.\n"+
                    "Deducted 20 copper coins")
        except Exception as e:
            print(e,", fight")


    async def event_monster(self, interaction: discord.Interaction):
        print("1")
        monster = util.rpg.generate_random_event(rpg_setting["monsters"])

        view = fight_or_run(interaction=interaction, monster=monster)
        embed = view.create_monster_embed()

        await interaction.followup.send(f"You encountered {monster}, do you want to fight?", embed=embed, view=view)


class fight_or_run(discord.ui.View):
    def __init__(self,interaction:discord.Interaction, monster:str):
        super().__init__()
        self.monster = monster
        self.player_detail = util.rpg.player_detail(interaction)
        self.monster_detail = util.rpg.monster_detail(monster)
        self.monster_agility = self.monster_detail["agility"] * util.rpg.bonus(self.player_detail)
        self.player_agility = self.player_detail["agility"]
        self.prob_of_battle = abs(self.player_agility-self.monster_agility) * 2 /max(self.player_agility,self.monster_agility)

    def create_monster_embed(self):
        embed = discord.Embed(title=f"Encounter: {self.monster}", description="What will you do?", color=discord.Color.red())
        embed.add_field(name="Monster Attack", value=self.monster_detail["attack"], inline=True)
        embed.add_field(name="Monster Defense", value=self.monster_detail["defense"], inline=True)
        embed.add_field(name="Monster Health", value=self.monster_detail["health"], inline=True)
        embed.add_field(name="Monster Agility", value=self.monster_detail["agility"], inline=True)
        embed.add_field(name="Escape Probability", value=f"{self.prob_of_battle:.2%}", inline=True)
        return embed

    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger)
    async def fight_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await fight.battle(fight, interaction, self.monster)
            
        except Exception as e:
            print(e, " ,fight button")

    @discord.ui.button(label="Run", style=discord.ButtonStyle.secondary)
    async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        try:
            self.monster_agility 
            if self.player_agility > 2 * self.monster_agility or self.monster_agility <= 0:
                await interaction.response.send_message("You successfully escaped!", ephemeral=True)
            elif self.monster_agility > 2 * self.player_agility or self.player_agility <= 0:
                await fight.battle(fight,self.player_detail,self.monster_detail)
            else:
                tmp = random.random()
                if self.prob_of_battle > tmp and self.monster_agility > self.player_agility:
                    fight.battle(fight,self.player_detail,self.monster_detail)
                else:
                    await interaction.response.send_message("You successfully escaped!", ephemeral=True)
        except Exception as e:
            print(e,", run")

