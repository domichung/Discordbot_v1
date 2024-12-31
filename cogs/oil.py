import discord
from discord.ext import commands
from discord import app_commands
import get_oil 
from datetime import timedelta

class Oil(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_oil_price(self, interaction: discord.Interaction, processed_data: str) -> None:
        embed = discord.Embed(
            title="本週油價",
            color=discord.Color.pink()
        )
        
        embed.add_field(
            name="查詢者",
            value=interaction.user.name,
            inline=False
        )
        
        embed.add_field(
            name="油價詳情",
            value=processed_data,
            inline=False
        )
        
        query_time = (discord.utils.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        footer_text = f"➤查詢時間: {query_time}"
        embed.set_footer(text=footer_text)
        
        await interaction.followup.send(embed=embed)

    @commands.command()
    async def oil(self, ctx: commands.Context):
        await ctx.send("油價查詢系統!")

    @app_commands.command(name="oil", description="查看本週油價")
    async def get_oil(self, interaction: discord.Interaction):
        try:
            rq_user = interaction.user.name
            oil_price_info = get_oil.get_oil_price()
            await interaction.response.send_message(f"{rq_user} 查詢了今日油價")

            await self.send_oil_price(interaction, oil_price_info)

        except Exception as e:
            await interaction.followup.send(
                f"fetch error：{str(e)} 請聯絡管理員",
                ephemeral=True
            )

    async def cog_app_command_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message("die = =", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Oil(bot))

