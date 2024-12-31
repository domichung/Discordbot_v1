import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta

class AnonymousMessageModal_main(discord.ui.Modal, title="匿名訊息發送"):
        
    message_content = discord.ui.TextInput(
        label="訊息內容",
        placeholder="訊息(雖為匿名發送但後臺留有數據請注意法律規範)",
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        message = self.message_content.value.strip()

        if not message:
            await interaction.response.send_message("訊息內容不能為空！", ephemeral=True)
            return

        source_channel = str(interaction.channel.id) if interaction.channel else "未知頻道"

        try:
            embed = discord.Embed(
                title="匿名喊話",
                description=message,
                color=discord.Color.gold() 
            )

            await interaction.channel.send(embed=embed)
            current_time = (discord.utils.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H:%M')
            
            message_data = {
                "message": message,
                "source_channel": source_channel,
                "sent_at": current_time,
                "sent_by": str(interaction.user.id)
            }

            try:
                try:
                    with open("anonymous_messages.json", "r", encoding="utf-8") as f:
                        messages = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    messages = []

                messages.append(message_data)

                with open("anonymous_messages.json", "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)

            except Exception as e:
                await interaction.response.send_message(f"保存訊息時發生錯誤：{str(e)}", ephemeral=True)

            await interaction.response.send_message(
                "訊息已成功發送到頻道！",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"發送訊息時發生錯誤：{str(e)}", ephemeral=True)

class AnonymousMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def AnonymousMessage(self, ctx: commands.Context):
        await ctx.send("匿名系統!")
        
    @app_commands.command(name="send_anonymous", description="發送匿名訊息")
    async def send_anonymous(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AnonymousMessageModal_main())

async def setup(bot: commands.Bot):
    await bot.add_cog(AnonymousMessage(bot))
