from discord.ext import tasks, commands
from datetime import timezone, datetime, timedelta
import json
import discord
from discord.utils import get

class SC_CLK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.check_events.start()
        self.u8_start_time = datetime.now(tz=timezone(timedelta(hours=8)))
        self.str_next_load_time = '2024-01-01-00:00:00'
        self.str_now_time = self.u8_start_time.strftime('%Y-%m-%d-%H:%M')
        self.bot = bot
        self.notified_events = set()  

    @commands.command()
    async def bord_timmer(self, ctx: commands.Context):
        await ctx.send("clock of board")

    def cog_unload(self):
        self.check_events.cancel()

    async def send_notification(self, event):
        """發送通知"""
        try:
            if event['notification_type'] == 'user':
                user = await self.bot.fetch_user(int(event['notification_target']))
                if user:
                    try:
                        embed = discord.Embed(
                            title="提醒：",
                            description=(f"事件：{event['event']}\n"
                                         f"地點：{event['location']}\n"
                                         f"開始時間：{event['starttime']}\n"
                                         f"結束時間：{event['endtime']}"),
                            color=discord.Color.green()
                        )
                        await user.send(embed=embed)
                        return True
                    except discord.Forbidden:
                        print(f"無法發送私訊給用戶 {user.name}")
                        return False
            elif event['notification_type'] == 'role':
                channel_id = int(event.get('source_channel', 0))
                if channel_id != 0:
                    try:
                        channel = await self.bot.fetch_channel(channel_id)
                        if channel:
                            try:
                                notification_target = event.get('notification_target')
                                if notification_target == "everyone":
                                    role_mention = "@everyone"
                                elif notification_target == "here":
                                    role_mention = "@here"
                                else:
                                    role = get(channel.guild.roles, name=notification_target)
                                    if role:
                                        role_mention = f"<@&{role.id}>"
                                    else:
                                        role_mention = "未找到角色"
                                embed = discord.Embed(
                                    title="提醒：",
                                    description=(f"{role_mention}\n"
                                                 f"事件：{event['event']}\n"
                                                 f"地點：{event['location']}\n"
                                                 f"開始時間：{event['starttime']}\n"
                                                 f"結束時間：{event['endtime']}"),
                                    color=discord.Color.green()
                                )
                                await channel.send(embed=embed)
                                return True
                            except discord.Forbidden:
                                print(f"無法在頻道 {channel.name} 發送訊息")
                                return False
                    except discord.NotFound:
                        print(f"頻道 {channel_id} 找不到")
                    except discord.Forbidden:
                        print(f"無法訪問頻道 {channel_id}")
            return False
        except Exception as e:
            print(f"發送通知時發生錯誤：{str(e)}")
            return False

    @tasks.loop(seconds=10)
    async def check_events(self):
        print("檢查時序表")
        try:
            with open("events.json", "r", encoding="utf-8") as f:
                events = json.load(f)

            current_time = datetime.now(tz=timezone(timedelta(hours=8)))
            current_time_str = current_time.strftime('%Y-%m-%d-%H:%M')

            events_to_remove = []
            
            self.notified_events.clear()

            for index, event in enumerate(events):
                if (event.get('bordtime') and 
                    event['bordtime'] <= current_time_str and 
                    event['bordtime'] not in self.notified_events):
                    
                    if await self.send_notification(event):
                        self.notified_events.add(event['bordtime'])
                        events_to_remove.append(index)

            for index in sorted(events_to_remove, reverse=True):
                events.pop(index)

            with open("events.json", "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"檢查事件時發生錯誤：{str(e)}")

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(SC_CLK(bot))
