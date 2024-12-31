import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
import wether as WG
from datetime import timedelta

class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_weather_forecast(self, interaction: discord.Interaction, processed_data: dict, search_city: str, updatetime) -> None:
        element_names = {
            'Wx': '天氣狀況',
            'MaxT': '最高溫度',
            'MinT': '最低溫度',
            'PoP': '降雨機率',
            'CI': '舒適度'
        }
        
        embed = discord.Embed(
            title=f"天氣預報資訊 - {search_city}",
            color=0x3498db  # blue
        )
        
        for time_slot, weather_data in sorted(processed_data.items()):
            field_value = ""
            for element, value in weather_data.items():
                field_value += f"**{element_names.get(element, element)}**: {value}\n"
            
            embed.add_field(
                name=f"時間：{time_slot}",
                value=field_value,
                inline=False
            )
        
        try:
            update_datetime = datetime.datetime.fromisoformat(updatetime)
            formatted_update_time = update_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_update_time = updatetime  
        
        query_time = (discord.utils.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        
        footer_text = f"➤查詢時間: {query_time} \n➤最後資料更新時間: {formatted_update_time}\n➤資料來源:中央氣象局開放API"
        embed.set_footer(text=footer_text)
        
        await interaction.followup.send(embed=embed)

    @commands.command()
    async def weather(self, ctx: commands.Context):
        await ctx.send("天氣系統!")

    # 設定天氣查詢指令
    @app_commands.command(name="weather", description="天氣查詢")
    @app_commands.describe(locations="選擇地區")
    @app_commands.choices(
        locations=[
            Choice(name="臺北市", value="taipei"),
            Choice(name="新北市", value="new_taipei"),
            Choice(name="桃園市", value="taoyuan"),
            Choice(name="臺中市", value="taichung"),
            Choice(name="臺南市", value="tainan"),
            Choice(name="高雄市", value="kaohsiung"),
            Choice(name="基隆市", value="keelung"),
            Choice(name="新竹縣", value="hsinchu_county"),
            Choice(name="新竹市", value="hsinchu_city"),
            Choice(name="苗栗縣", value="miaoli"),
            Choice(name="彰化縣", value="changhua"),
            Choice(name="南投縣", value="nantou"),
            Choice(name="雲林縣", value="yunlin"),
            Choice(name="嘉義縣", value="chiayi_county"),
            Choice(name="嘉義市", value="chiayi_city"),
            Choice(name="屏東縣", value="pingtung"),
            Choice(name="宜蘭縣", value="yilan"),
            Choice(name="花蓮縣", value="hualien"),
            Choice(name="臺東縣", value="taitung"),
            Choice(name="澎湖縣", value="penghu"),
            Choice(name="金門縣", value="kinmen"),
            Choice(name="連江縣", value="lienchiang"),
        ]
    )
    async def re_weather(self, interaction: discord.Interaction, locations: Choice[str]):
        try:
            rq_user = interaction.user.name
            locate = locations.name
            
            await interaction.response.send_message(f"{rq_user} 查詢了 {locate} 地區的天氣")
            
            weather_data, updatetime = WG.check_weather(locate)
            
            await self.send_weather_forecast(interaction, weather_data, locate, updatetime)
            
        except Exception as e:
            await interaction.followup.send(
                f"fatch error：{str(e)} 請聯絡管理員",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Weather(bot))