import discord
from discord.ext import commands
from discord import app_commands

# 定義名為 Main 的 Cog
class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # name指令名稱，description指令敘述
    @app_commands.command(name = "hello", description = "Hello, world!")
    async def hello(self, interaction: discord.Interaction):
    # 回覆使用者的訊息
        await interaction.response.send_message("Hello, world!")

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))