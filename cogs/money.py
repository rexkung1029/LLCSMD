import discord
import json
import os

from discord import app_commands
from discord.ext import commands

def money_guild(guild:discord.Guild):
    return(f"{str(guild.id)},{guild.name}")

def json_write(path:str, file):
    try:
        with open(path,'w',encoding='utf8') as tmp:
            json.dump(file, tmp, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e,", json_w")

class Money(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name="money")
    async def money(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"您擁有{self.get_money(interaction)}元")

    async def initialize_money_records(self):
        try:
            json_file_path = 'money_records.json'

            if not os.path.exists(json_file_path):
                data = {}
                json_write(json_file_path, data)
            else:
                with open(json_file_path, 'r', encoding='utf8') as f:
                    data = json.load(f)
            
            guild_count:int = 0
            guilds = self.bot.fetch_guilds(limit=None, with_counts=True)
            async for guild in guilds:
                guild: discord.Guild = await self.bot.fetch_guild(guild.id)
                if str(guild.id) not in data:
                    data[money_guild(guild)] = {}
                    json_write(json_file_path, data)
                guild_count += 1
                member_count:int = 0
                guild = self.bot.get_guild(guild.id)
                for member in guild.members:
                    if not member.bot:
                        user_id = str(member.id)
                        if user_id not in data[money_guild(guild)]: 
                            data[money_guild(guild)][user_id] = 0
                        member_count += 1

            json_write(json_file_path, data)
        except Exception as e:
            print(e,", money")

    def money_add(self, count: int, guild, user: int):
        with open("money_records.json","r",encoding="utf8") as m:
            m_data = json.load(m)
        money = m_data[money_guild(guild)][str(user)]
        money += count
        m_data[money_guild(guild)][str(user)] = money
        json_write("money_records.json",m_data)

    def get_money(self, interaction:discord.Interaction) -> int : 
        try:
            with open("money_records.json","r",encoding="utf8") as m:
                m_data = json.load(m)
            money = m_data[money_guild(interaction.guild)][str(interaction.user.id)]
            return money
        except Exception as e:print(e,",m get money")

async def setup(bot: commands.Bot):
    await bot.add_cog(Money(bot))