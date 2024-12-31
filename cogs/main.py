import discord
from discord.ext import commands

# 定義名為 Main 的 Cog
class main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def Help_Admin(self, ctx: commands.Context):
        await ctx.send("--------管理指令列表--------")
        await ctx.send("$unload {function}")
        await ctx.send("$load {function}")
        await ctx.send("$reload {function}")
        await ctx.send('-'*30)
        
    @commands.command()
    async def show_load(self, ctx: commands.Context):
        await ctx.send("因為unix 課程教的系統控制讓我想到可以寫這個東西")
        #await ctx.send("教授教得真  的是太好了 5星好評(膜拜教授)")
        
# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(main(bot))