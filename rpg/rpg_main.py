import discord
import random
import math
import json

from discord.ext import commands,tasks
from discord import app_commands
from discord.app_commands import Choice

j_stats_p = "rpg/rpg_stats.json"
exploring = []

with open(j_stats_p,"r",encoding="utf8") as tmp:
    rpg_stats = json.load(tmp)

def json_write(path:str, file):
    try:
        with open(path,'w',encoding='utf8') as tmp:
            json.dump(file, tmp, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e,", json_w")


class rpg_main(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @app_commands.command(name="rpg")
    @app_commands.choices(
        opt=[
            Choice(name="start", value="start"),
            Choice(name="explore", value="explore")
        ]
    )
    async def rpg(self, interaction: discord.Interaction, opt: str=None):
        try:
            if opt == "start":
                if str(interaction.guild_id) not in rpg_stats:
                    rpg_stats[str(interaction.guild_id)] = {}
                    json_write(j_stats_p,rpg_stats)
                    
                if str(interaction.user.id) not in rpg_stats[str(interaction.guild_id)]:
                    rpg_stats[str(interaction.guild_id)][str(interaction.user.id)] = {
                        "name":interaction.user.nick or interaction.user.name,
                        "level": 1,
                        "inventory":{},
                        "skills":{},
                        "experience": 0,
                        "health": 100,
                        "mana": 100,
                        "depth": 1
                    }
                    json_write(j_stats_p,rpg_stats)
                    await interaction.response.send_message("成功建立角色", ephemeral=True)
                else:              
                    await interaction.response.send_message("你已經擁有角色", ephemeral=True)

            elif opt == "explore":
                if interaction.user.id not in exploring:
                    await interaction.response.send_message("開始探索", ephemeral=True)
                else:
                    await interaction.response.send_message("繼續探索", ephemeral=True)
                await self.new_event(interaction)
        except Exception as e:
            print(e, ", rpg")

#-----事件----------事件----------事件----------事件-----
    async def event_monster(self, interaction):
        self.monster =  {
            "哥布林": 0.49,
            "巨魔": 0.25,
            "食人魔": 0.2,
            "狼人": 0.1,
            "巨龍": 0.01
        }
    async def event_treasure_chest(self, interaction):
        pass
    async def event_special_room(self, interaction):
        pass
    async def event_stairs(self, interaction):
        pass
    async def execute_event(self,event_name, interaction):
        self.event_functions = {
            "monster": self.event_monster,
            "treasure chest": self.event_treasure_chest,
            "special_room": self.event_special_room,
            "stairs": self.event_stairs
        }

        if event_name in self.event_functions:
            return self.event_functions[event_name](interaction)
        else:
            return "未知事件"



    def generate_random_event(self,events:dict):
        rand = random.random()
        cumulative_probability = 0.0

        for event, probability in events.items():
            cumulative_probability += probability
            if rand < cumulative_probability:
                return event
        return None
    
    async def new_event(self, interaction:discord.Interaction):
        self.events_msg = {
            "monster": "你遇到了怪物！",
            "treasure chest": "你發現了一個寶箱！",
            "special_room": "你遇見了神奇房間！",
            "stairs": "你找到了通往下一層的樓梯！"
        }
        events = {
            "monster": 0.65,
            "treasure chest": 0.15,
            "special_room": 0.15,
            "stairs": 0.05  
        }
        event = self.generate_random_event(events)
        if event:
            event_message = self.events_msg[event]
            await interaction.followup.send(f"{event_message}", ephemeral= True)
            await self.execute_event(event_name=event, interaction=interaction)

        else:
            await interaction.followup.send("沒有發生任何事件。", ephemeral= True)



async def setup(bot: commands.Bot):
    await bot.add_cog(rpg_main(bot))