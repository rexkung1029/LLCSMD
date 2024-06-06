import json,asyncio,discord,datetime,os

from cogs.games import *
from discord.ext import commands,tasks
from discord import app_commands

with open('setting.json','r',encoding='utf8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = ("!","0","?"),intents=intents)



@bot.event
async def on_ready():
    try:
        money = Money(bot)

        with open('setting.json','w',encoding='utf8') as tmp:
            json.dump(jdata,tmp,indent=4,ensure_ascii=False)

        await money.initialize_money_records()

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
    await ctx.send("Synced")

@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def load(ctx:commands.Context, extension:str):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def unload(ctx:commands.Context, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.")

@bot.hybrid_command()
@commands.is_owner()
@app_commands.choices(
    extension=[app_commands.Choice(name=ext[:-3], value=ext[:-3]) for ext in os.listdir('./cogs') if ext.endswith('.py')]
)
async def reload(ctx:commands.Context, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")


@bot.hybrid_command()   
@commands.is_owner()  
async def shutdown(ctx):
    await ctx.send("機器人將關閉。")
    await bot.close()

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.startswith("-"):
            continue
        elif filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"cogs.{filename[:-3]} loaded")

async def main():
    async with bot:
        await load_extensions()
        with open('token.json','r',encoding='utf8') as t:
            token = json.load(t)
        await bot.start(token['discord']['Token'])

if __name__ == "__main__":
    asyncio.run(main())