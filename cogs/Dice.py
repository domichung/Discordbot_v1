import discord
from discord.ext import commands
from discord import app_commands
import random

class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def get_dice_face(self, num: int) -> str:
        match num:
            case 1:
                return "⚀"
            case 2:
                return "⚁"
            case 3:
                return "⚂"
            case 4:
                return "⚃"
            case 5:
                return "⚄"
            case 6:
                return "⚅"
            case _:
                return str(num)


    @commands.command()
    async def rowdice(self, ctx: commands.Context):
        await ctx.send("丟骰子")
        
    @app_commands.command(name="rowdice", description="擲骰子指令")
    @app_commands.describe(num="要擲的骰子數量 (1-100)")
    async def dice(self, interaction: discord.Interaction, num: int):
        try:
            if not 1 <= num <= 100:
                await interaction.response.send_message(
                    "請輸入 1-10 之間的數字！",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            results = [random.randint(1, 6) for _ in range(num)]
            dice_faces = [self.get_dice_face(result) for result in results]
            total = sum(results)
            
            embed = discord.Embed(
                title="🎲 擲骰子結果",
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="擲骰者",
                value=interaction.user.name,
                inline=False
            )
            
            embed.add_field(
                name="骰子數量",
                value=str(num),
                inline=True
            )
            
            embed.add_field(
                name="總值",
                value=str(total),
                inline=True
            )
            
            embed.add_field(
                name="結果",
                value='、'.join(dice_faces),
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"發生錯誤：{str(e)} 請聯絡管理員",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"發生錯誤：{str(e)} 請聯絡管理員",
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(Dice(bot))