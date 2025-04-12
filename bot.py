import os
import asyncio
import discord
from discord.ext import commands
import tk

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "$", intents = intents)

# 當機器人完成啟動時
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="自己的尾巴！"))
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")

# 載入指令程式檔案
@bot.command()
async def load(ctx, extension):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"載入 {extension} 成功")
    except:
        await ctx.send(f"載入 {extension} 失敗")
        
# 卸載指令檔案
@bot.command()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"卸載 {extension} 成功")
    except:
        await ctx.send(f"卸載 {extension} 失敗")
    
# 重新載入程式檔案
@bot.command()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"重載 {extension} 成功")
    except:
        await ctx.send(f"重載 {extension} 失敗")
        
# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(filename)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(tk.get_token())

# 確定執行此py檔才會執行
if __name__ == "__main__":
    asyncio.run(main())
