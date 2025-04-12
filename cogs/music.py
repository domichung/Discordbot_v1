import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import json
import asyncio
from typing import Dict, List

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
}
yt_dl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

class MusicControls(discord.ui.View):
    def __init__(self, music_cog, guild_id: int):
        super().__init__(timeout=None)
        self.music_cog = music_cog
        self.guild_id = guild_id

    @discord.ui.button(label="⏯️ 播放/暫停", style=discord.ButtonStyle.primary)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message("我不在語音頻道內", ephemeral=True)
            return

        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ 已繼續播放", ephemeral=True)
        elif vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ 已暫停播放", ephemeral=True)
        else:
            await interaction.response.send_message("目前沒有正在播放的音樂", ephemeral=True)

    @discord.ui.button(label=" ⏭️ 下一首 ", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message("我不在語音頻道內", ephemeral=True)
            return

        queue = self.music_cog.queue.get(self.guild_id, [])
        if queue:
            vc.stop()
            await interaction.response.send_message("⏭️ 已跳過", ephemeral=True)
        else:
            await interaction.response.send_message("播放清單是空的", ephemeral=True)

    @discord.ui.button(label="📋 播放清單 ", style=discord.ButtonStyle.success)
    async def show_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = self.music_cog.queue.get(self.guild_id, [])
        if not queue:
            await interaction.response.send_message("播放清單是空的", ephemeral=True)
            return

        queue_list = "\n".join(f"{i+1}. {song['title']}" for i, song in enumerate(queue))
        await interaction.response.send_message(f"📋 播放清單：\n{queue_list}", ephemeral=True)

    @discord.ui.button(label="👋 離開頻道 ", style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            self.music_cog.queue[self.guild_id] = []
            await interaction.response.send_message("👋 已離開語音頻道", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("我不在語音頻道中", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue: Dict[int, List[dict]] = {}
        self.current_channel: Dict[int, discord.TextChannel] = {}

    async def play_next(self, guild: discord.Guild):
        if self.queue.get(guild.id):
            song = self.queue[guild.id].pop(0)
            vc = guild.voice_client
            if not vc:
                return

            try:
                audio = discord.FFmpegOpusAudio(song['url'], **ffmpeg_options)
                vc.play(audio, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(guild), self.bot.loop))

                if self.current_channel.get(guild.id):
                    view = MusicControls(self, guild.id)
                    await self.current_channel[guild.id].send(f"🎵 正在播放: {song['title']}", view=view)
            except Exception as e:
                print(f"播放失敗: {e}")
                await vc.disconnect()

    @app_commands.command(name="play", description="播放 YouTube 音樂")
    async def play(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("請先加入語音頻道！", ephemeral=True)
            return

        await interaction.response.defer()
        guild = interaction.guild
        channel = interaction.user.voice.channel

        if not guild.voice_client:
            await channel.connect()

        self.current_channel[guild.id] = interaction.channel
        if guild.id not in self.queue:
            self.queue[guild.id] = []

        try:
            data = ytdl.extract_info(url, download=False)
            song_url = data['url']
            song_title = data['title']
        except Exception as e:
            await interaction.followup.send(f"❌ 無法取得音樂資訊：{e}")
            return

        song_info = {'url': song_url, 'title': song_title}

        vc = guild.voice_client
        if not vc.is_playing():
            audio = discord.FFmpegOpusAudio(song_url, **ffmpeg_options)
            vc.play(audio, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(guild), self.bot.loop))

            view = MusicControls(self, guild.id)
            await interaction.followup.send(f"🎵 正在播放: {song_title}", view=view)
        else:
            self.queue[guild.id].append(song_info)
            await interaction.followup.send(f"✅ 已加入播放清單: {song_title}")

    @app_commands.command(name="queue", description="查看播放清單")
    async def queue_cmd(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        queue = self.queue.get(guild_id, [])
        if not queue:
            await interaction.response.send_message("播放清單是空的")
            return

        queue_list = "\n".join(f"{i+1}. {song['title']}" for i, song in enumerate(queue))
        await interaction.response.send_message(f"📋 播放清單：\n{queue_list}")

    @app_commands.command(name="leave", description="讓機器人離開語音頻道")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            self.queue[interaction.guild.id] = []
            await interaction.response.send_message("👋 已離開語音頻道")
        else:
            await interaction.response.send_message("我不在語音頻道內", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))

