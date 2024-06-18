import asyncio
import discord
import json
import os

from discord import app_commands
from discord.ext import commands

with open('setting.json','r',encoding='utf8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = ("!","0","?"),intents=intents)


@bot.event
async def on_ready():
    try:
        with open('setting.json','w',encoding='utf8') as tmp:
            json.dump(jdata,tmp,indent=4,ensure_ascii=False)
        print("syncing...")
        await bot.tree.sync()
        print(">>Bot is online<<")
        print('Client ID:', bot.user.id)
        print('Client Name:', bot.user.name)
    except Exception as e:
        print(e,", on ready")


@bot.hybrid_command()
async def sync(ctx:commands.Context):
    await ctx.send('Syncing...')
    await bot.tree.sync()
    await ctx.channel.send("Synced")


@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def load(ctx:commands.Context, extension:str):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.",ephemeral=True)


@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def unload(ctx:commands.Context, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.",ephemeral=True)


@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def reload(ctx:commands.Context, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.",ephemeral=True)


@bot.hybrid_command()
@commands.is_owner()
async def reload_rpg(ctx:commands.Context):
    await bot.reload_extension("Rpg.rpg_main")
    await ctx.send("Reload RPG done.",ephemeral=True)


@bot.hybrid_command()   
@commands.is_owner()  
async def shutdown(ctx:commands.Context):
    await ctx.send("機器人將關閉。",ephemeral=True)
    await bot.close()


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.startswith("-"):
            continue
        elif filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"cogs.{filename[:-3]} loaded")
    await bot.load_extension("Rpg.rpg_main")
    print("Rpg.rpg_main loaded")


async def main():
    async with bot:
        await load_extensions()
        with open('token.json','r',encoding='utf8') as t:
            token = json.load(t)
        await bot.start(token['discord']['Token'])

if __name__ == "__main__":
    asyncio.run(main())
