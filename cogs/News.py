import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import news_etoday
import news_now
import news_yahoo
from datetime import timedelta


class News(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_news_forecast(self, interaction: discord.Interaction, processed_data: dict, newsfrom: str) -> None:

        embed = discord.Embed(
            title=f"新聞 - {newsfrom}",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="查詢者",
            value=interaction.user.name,
            inline=False
        )
                      
        embed.add_field(
            name="熱點新聞",
            value=processed_data,
            inline=False
        )
              
        query_time = (discord.utils.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        
        footer_text = f"➤查詢時間: {query_time}\n➤資料來源:{newsfrom}"
        embed.set_footer(text=footer_text)
        print("send news")
        await interaction.followup.send(embed=embed)

    @commands.command()
    async def news(self, ctx: commands.Context):
        await ctx.send("新聞系統!")

    @app_commands.command(name="news", description="查看今日新聞")
    @app_commands.describe(locations="選擇新聞來源")
    @app_commands.choices(
        locations=[
            Choice(name="Yahoo奇摩新聞", value="yahoo-news"),
            Choice(name="ETtoday新聞雲", value="etoday-news"),
            Choice(name="NOWnews今日新聞", value="now-news"),
        ]
    )
    async def get_news(self, interaction: discord.Interaction, locations: Choice[str]):
        try:
            rq_user = interaction.user.name
            locate_ch = locations.name
            locate_en = locations.value
            
            if (locate_en == 'yahoo-news'):
                n = news_yahoo.loadnews(20)
            elif (locate_en == 'etoday-news'):
                n = news_etoday.loadnews(20)
            elif (locate_en == 'now-news'):
                n = news_now.get_news(20)
            else:
                n = "error 請聯絡管理員"
                
            await interaction.response.send_message(f"{rq_user} 查詢了 {locate_ch} 的新聞")
            
            await self.send_news_forecast(interaction, n, locate_ch)
            
        except Exception as e:
            await interaction.followup.send(
                f"fatch error：{str(e)} 請聯絡管理員",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(News(bot))