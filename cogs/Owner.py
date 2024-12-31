import discord
from discord.ext import commands
from discord import app_commands
import json

class Owner(commands.Cog):
    @commands.command()
    async def Owner(self, ctx: commands.Context):
        await ctx.send("主人歡迎回家")
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner_file = "Owner.json"

    async def load_owners(self):
        try:
            with open(self.owner_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    async def save_owners(self, owners):
        with open(self.owner_file, "w", encoding="utf-8") as f:
            json.dump(owners, f, ensure_ascii=False, indent=4)

    @app_commands.command(name="tame", description="註冊為主人")
    async def tame(self, interaction: discord.Interaction):
        owners = await self.load_owners()

        if interaction.user.id not in owners:
            owners.append(interaction.user.id)
            await self.save_owners(owners)
            await interaction.response.send_message(f"{interaction.user.name} 成為了我的主人！", ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.name} 已經是我的主人了！", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        owners = await self.load_owners()
        if message.author.id in owners:
            if "我回來了" in message.content:
                await message.channel.send(file=discord.File("photo/back.jpg"))
                await message.channel.send("主人歡迎回家")

            elif "喵" in message.content:
                await message.channel.send("喵喵!")
                
            elif "咕嚕靈波" in message.content:
                await message.channel.send(file=discord.File("photo/gurulinbo.gif"))
                await message.channel.send("咕嚕靈波❤️")

            elif "變好吃的魔法" in message.content:
                await message.channel.send(file=discord.File("photo/goodtoeat.jpg"))
                await message.channel.send("萌え萌えキュン❤️")
                
async def setup(bot: commands.Bot):
    await bot.add_cog(Owner(bot))
