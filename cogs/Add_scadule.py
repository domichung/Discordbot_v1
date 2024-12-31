import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta

class Add_scadule_main(discord.ui.Modal, title="事件提醒設定"):
        
    event_thing = discord.ui.TextInput(
        label="事件 (事件/地點)",
        placeholder="例：團練/練團室 或 團練",
        max_length=100,
        required=True
    )
    event_start_time = discord.ui.TextInput(
        label="事件開始 (YYYY-MM-DD-HH:MM)",
        placeholder="2024-12-28-14:00",
        required=True
    )
    event_end_time = discord.ui.TextInput(
        label="事件結束 (留空表示永久)",
        placeholder="2024-12-28-16:00",
        required=False
    )
    bordteam = discord.ui.TextInput(
        label="通知對象 (self/@身分組名稱)",
        required=False,
        placeholder="self 或 @管理員"
    )
    bord_time = discord.ui.TextInput(
        label="通知時間 (YYYY-MM-DD-HH:MM)",
        required=False,
        placeholder="2024-12-28-13:30"
    )

    def validate_datetime(self, datetime_str: str) -> bool:
        try:
            datetime.strptime(datetime_str, "%Y-%m-%d-%H:%M")
            return True
        except ValueError:
            return False

    def parse_event_location(self, event_input: str) -> tuple[str, str]:
        if '/' in event_input:
            event, location = event_input.split('/', 1)
            return event.strip(), location.strip()
        else:
            return event_input.strip(), "地球中的某個角落"

    def process_notification_target(self, target: str, interaction: discord.Interaction) -> tuple[str, str]:
        """處理通知對象，返回類型和ID/名稱"""
        if not target:
            return '', ''
            
        target = target.strip()
        
        if target.lower() == 'self':
            return 'user', str(interaction.user.id)
        
        if target.startswith('@'):
            target = target[1:]
        return 'role', target

    async def on_submit(self, interaction: discord.Interaction):
        if not self.validate_datetime(self.event_start_time.value):
            await interaction.response.send_message("開始時間格式錯誤！請使用YYYY-MM-DD-HH:MM格式", ephemeral=True)
            return
        
        if self.event_end_time.value and not self.validate_datetime(self.event_end_time.value):
            await interaction.response.send_message("結束時間格式錯誤！請使用YYYY-MM-DD-HH:MM格式", ephemeral=True)
            return

        if self.bord_time.value and not self.validate_datetime(self.bord_time.value):
            await interaction.response.send_message("通知時間格式錯誤！請使用YYYY-MM-DD-HH:MM格式", ephemeral=True)
            return

        start_time = datetime.strptime(self.event_start_time.value, "%Y-%m-%d-%H:%M")
        if self.event_end_time.value:
            end_time = datetime.strptime(self.event_end_time.value, "%Y-%m-%d-%H:%M")
            if start_time >= end_time:
                await interaction.response.send_message("開始時間必須早於結束時間！", ephemeral=True)
                return

        event, location = self.parse_event_location(self.event_thing.value)

        notification_type, notification_target = self.process_notification_target(
            self.bordteam.value if self.bordteam.value else '', 
            interaction
        )

        current_time = (discord.utils.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H:%M')

        source_channel = str(interaction.channel.id) if interaction.channel else "未知頻道"

        event_data = {
            "event": event,
            "location": location,
            "starttime": self.event_start_time.value,
            "endtime": self.event_end_time.value if self.event_end_time.value else "直到世界末日",
            "notification_type": notification_type,
            "notification_target": notification_target,
            "bordtime": self.bord_time.value if self.bord_time.value else None,
            "created_at": current_time,
            "created_by": str(interaction.user.id),
            "source_channel": source_channel
        }

        try:
            try:
                with open("events.json", "r", encoding="utf-8") as f:
                    events = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                events = []

            events.append(event_data)

            with open("events.json", "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=4)

            notification_display = "無"
            if notification_type == 'user':
                notification_display = f"用戶 ID: {notification_target}"
            elif notification_type == 'role':
                notification_display = f"身分組: {notification_target}"

            await interaction.response.send_message(
                f"事件已成功保存！\n"
                f"事件：{event}\n"
                f"地點：{location}\n"
                f"開始時間：{self.event_start_time.value}\n"
                f"結束時間：{event_data['endtime']}\n"
                f"通知對象：{notification_display}\n"
                f"通知時間：{self.bord_time.value if self.bord_time.value else '無'}\n"
                f"來源頻道：{source_channel}\n"
                f"創建時間：{current_time}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(f"保存事件時發生錯誤：{str(e)}", ephemeral=True)

class Add_scadule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set_event", description="設置事件提醒")
    async def set_event(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Add_scadule_main())
        
    @commands.command()
    async def Add_scadule(self, ctx: commands.Context):
        await ctx.send("排程")

async def setup(bot: commands.Bot):
    await bot.add_cog(Add_scadule(bot))
