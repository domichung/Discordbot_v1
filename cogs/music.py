import discord
from discord.ext import commands
import yt_dlp
from discord.app_commands import CommandTree
from typing import Dict, List

class MusicControls(discord.ui.View):
    def __init__(self, music_cog, current_song: str):
        super().__init__(timeout=None)
        self.music_cog = music_cog
        self.current_song = current_song

    @discord.ui.button(label="⏯️ 播放/暫停", style=discord.ButtonStyle.primary)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            await interaction.response.send_message("目前沒有在播放音樂", ephemeral=True)
            return

        if voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ 繼續播放", ephemeral=True)
        elif voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ 已暫停", ephemeral=True)
        else:
            await interaction.response.send_message("目前沒有音樂正在播放", ephemeral=True)

    @discord.ui.button(label="⏭️ 下一首", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("目前沒有在播放音樂", ephemeral=True)
            return

        if self.music_cog.queue.get(interaction.guild_id):
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("⏭️ 跳過當前歌曲", ephemeral=True)
        else:
            await interaction.response.send_message("播放清單中沒有下一首歌", ephemeral=True)

    @discord.ui.button(label="📋 播放清單", style=discord.ButtonStyle.success)
    async def show_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild_id
        if not self.music_cog.queue.get(guild_id):
            await interaction.response.send_message("播放清單是空的", ephemeral=True)
            return

        queue_text = f"🎵 正在播放: {self.current_song}\n\n📋 播放清單:\n"
        queue_list = "\n".join(
            f"{i+1}. {song['title']}" 
            for i, song in enumerate(self.music_cog.queue[guild_id])
        )
        await interaction.response.send_message(f"{queue_text}{queue_list}", ephemeral=True)

    @discord.ui.button(label="👋 離開頻道", style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            self.music_cog.is_playing[interaction.guild_id] = False
            self.music_cog.queue[interaction.guild_id].clear()
            await interaction.response.send_message("👋 已離開語音頻道", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("機器人不在語音頻道中", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = {}
        self.queue: Dict[int, List[dict]] = {}
        self.current_channel = {}
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'retries': 5,
            'socket_timeout': 10
        }

    async def send_new_player(self, channel, guild_id: int, song_title: str):
        view = MusicControls(self, song_title)
        message = await channel.send(
            f"🎵 正在播放: {song_title}\n\n使用下方按鈕控制播放:",
            view=view
        )
        return message

    async def after_playing(self, guild_id: int):
        if guild_id in self.queue and self.queue[guild_id]:
            next_song = self.queue[guild_id].pop(0)
            voice = self.bot.get_guild(guild_id).voice_client
            if voice:
                voice.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(next_song['url'],
                        options="-vn -buffer_size 64K -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                    )),
                    after=lambda e: self.bot.loop.create_task(self.after_playing(guild_id))
                )

                if guild_id in self.current_channel:
                    channel = self.current_channel[guild_id]
                    await self.send_new_player(channel, guild_id, next_song['title'])

    @discord.app_commands.command(name="play", description="播放YouTube音樂")
    async def play(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice:
            await interaction.response.send_message("請先加入語音頻道！")
            return

        try:
            await interaction.response.defer()
            channel = interaction.user.voice.channel
            guild_id = interaction.guild_id
            self.current_channel[guild_id] = interaction.channel

            if guild_id not in self.queue:
                self.queue[guild_id] = []

            if not interaction.guild.voice_client:
                voice = await channel.connect()
            else:
                voice = interaction.guild.voice_client

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'url': info['url'],
                    'title': info['title']
                }

            if not voice.is_playing():
                voice.play(discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song_info['url'],
                        options="-vn -buffer_size 64K -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                    )),
                    after=lambda e: self.bot.loop.create_task(self.after_playing(guild_id))
                )
                self.is_playing[guild_id] = True
                await self.send_new_player(interaction.channel, guild_id, song_info['title'])
                await interaction.followup.send("✅ 已開始播放", ephemeral=True)
            else:
                self.queue[guild_id].append(song_info)
                await interaction.followup.send(f"🎵 已加入播放清單: {song_info['title']}")

        except Exception as e:
            await interaction.followup.send(f"發生錯誤: {str(e)}")
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
            self.is_playing[guild_id] = False

    @discord.app_commands.command(name="queue", description="顯示播放清單")
    async def queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not self.queue.get(guild_id):
            await interaction.response.send_message("播放清單是空的")
            return

        queue_list = "\n".join(
            f"{i+1}. {song['title']}" 
            for i, song in enumerate(self.queue[guild_id])
        )
        await interaction.response.send_message(f"播放清單:\n{queue_list}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
