import discord
import re
import asyncio
import yt_dlp
import time
import urllib.parse
import urllib.request

from discord.ext import commands, tasks

class Youtube(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.youtube_base_url = 'https://www.youtube.com/'
        self.youtube_results_url = self.youtube_base_url + 'results?'
        self.youtube_watch_url = self.youtube_base_url + 'watch?v='
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

        self.check_voice_channel.start()

    @tasks.loop(seconds=60)  # 每60秒檢查一次
    async def check_voice_channel(self):
        for guild_id, voice_data in list(self.voice_clients.items()):
            if voice_data["client"].is_connected() and len(voice_data["client"].channel.members) == 1:  # 如果只剩機器人
                await voice_data["client"].disconnect()
                del self.voice_clients[guild_id]

    @commands.command(name="play", aliases=["p","pl"])
    async def play(self, ctx:commands.Context, *, link):
        try:
            
            link = self.url_format(url=link)

            if "www.youtube.com" not in link:
                return

            if not ctx.guild.id in self.voice_clients or not self.voice_clients[ctx.guild.id]["client"].is_connected():
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[ctx.guild.id] = {"client": voice_client}
                print("start playing")
            else:
                print("start function queue")
                await self.queue(ctx, url=link)
                return

            await self._play(ctx, link)
        except Exception as e:
            print(e,", play")

    async def _play(self, ctx: commands.Context, link):
        try:
            # 確認是否能播放
            loop = asyncio.get_event_loop()
            await ctx.channel.send("正在載入")
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

            song_url = data['url']
            title = data['title']
            duration = data['duration']  # in seconds
            thumbnail = data.get('thumbnail', '')

            player = discord.FFmpegOpusAudio(song_url, **self.ffmpeg_options)
            self.voice_clients[ctx.guild.id]["client"].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

            embed = discord.Embed(title=title, description="播放中...", color=0xadc8ff)
            embed.set_thumbnail(url=thumbnail)
            embed_msg = await ctx.send(embed=embed)

            self.voice_clients[ctx.guild.id]["embed"] = embed
            self.voice_clients[ctx.guild.id]["embed_msg"] = embed_msg
            self.voice_clients[ctx.guild.id]["start_time"] = time.time()
            self.voice_clients[ctx.guild.id]["duration"] = duration

            while self.voice_clients[ctx.guild.id]["client"].is_playing():
                elapsed_time = int(time.time() - self.voice_clients[ctx.guild.id]["start_time"])

                elapsed_formatted = self.format_time(elapsed_time)
                duration_formatted = self.format_time(duration)

                progress_bar = self.generate_progress_bar(elapsed_time, duration, length=20)

                embed.description = f"播放中...\n{progress_bar} {elapsed_formatted}/{duration_formatted}"
                await embed_msg.edit(embed=embed)
                await asyncio.sleep(2)  # Update every 2 seconds

        except Exception as e:
            print(e, "play2")

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins}:{secs:02}"

    def generate_progress_bar(self, elapsed, total, length=20):
        progress = elapsed / total
        num_ticks = round(length * progress)
        num_spaces = length - num_ticks - 1
        return '[' + '-' * num_ticks + '•' + "-" * num_spaces + ']'

    async def play_next(self, ctx:commands.Context):
        try:
            if "embed_msg" in self.voice_clients[ctx.guild.id]:
                try:
                    await self.voice_clients[ctx.guild.id]["embed_msg"].delete()
                except discord.NotFound:
                    pass
            
            # 檢查是否有下一首歌曲在隊列中
            if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                # 從隊列中取出下一首歌曲
                next_song = self.queues[ctx.guild.id].pop(0)["url"]
                print(next_song)
                # 播放下一首歌曲
                await self._play(ctx, link=next_song)
                print("下一首")
            else:
                await ctx.channel.send("播放完畢")
                await self.stop(ctx)
        except Exception as e:
            print(e, ", play_next")

    @commands.command(name="clear_queue", aliases=["cq"])
    async def clear_queue(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send("佇列已清空")
        else:
            await ctx.send("佇列為空")

    @commands.command(name="pause")
    async def pause(self, ctx):
        try:
            elapsed_time = int(time.time() - self.voice_clients[ctx.guild.id]["start_time"])

            elapsed_formatted = self.format_time(elapsed_time)
            duration_formatted = self.format_time(self.voice_clients[ctx.guild.id]["duration"])

            progress_bar = self.generate_progress_bar(elapsed_time, self.voice_clients[ctx.guild.id]["duration"], length=20)

            self.voice_clients[ctx.guild.id]["embed"].description = f"已暫停\n{progress_bar} {elapsed_formatted}/{duration_formatted}"
            await self.voice_clients[ctx.guild.id]["embed_msg"].edit(embed=self.voice_clients[ctx.guild.id]["embed"])

            self.voice_clients[ctx.guild.id]["client"].pause()
        except Exception as e:
            print(e)

    @commands.command(name="resume", aliases=["r"])
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id]["client"].resume()
            while self.voice_clients[ctx.guild.id].is_playing():
                elapsed_time = int(time.time() - self.start_time)
                elapsed_formatted = self.format_time(elapsed_time)
                duration_formatted = self.format_time(self.duration)
                progress_bar = self.generate_progress_bar(elapsed_time, self.duration, length=20)
                self.embed.description = f"播放中...\n{progress_bar} {elapsed_formatted}/{duration_formatted}"
                await self.embed_msg.edit(embed=self.embed)
                await asyncio.sleep(2)
        except Exception as e:
            print(e)

    @commands.command(name="stop")
    async def stop(self, ctx:commands.Context):
        try:
            if "embed_msg" in self.voice_clients[ctx.guild.id]:
                try:
                    await self.voice_clients[ctx.guild.id]["embed_msg"].delete()
                except discord.NotFound:
                    pass

            self.voice_clients[ctx.guild.id]["client"].stop()
            await self.voice_clients[ctx.guild.id]["client"].disconnect()
            del self.voice_clients[ctx.guild.id]
        except Exception as e:
            print(e)

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx, *, url):
        try:
            url = self.url_format(url=url)
            if "list" in url:
                await ctx.send("禁止使用播放清單")
                return
 
            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []

            if len(self.queues[ctx.guild.id]) >= 25:
                await ctx.send("佇列已滿25首，請等待當前歌曲播放完畢後再嘗試添加新的歌曲。")
                return

            data = self.ytdl.extract_info(url, download=False)
            title = data.get('title', 'Unknown Title')

            self.queues[ctx.guild.id].append({"url": url, "title": title})
            print(f"加入歌曲{title}")
            await ctx.send(f"{title}加入佇列!")
        except Exception as e:
            print(e,", queue")

    @commands.command(name="list_queue", aliases=["lq"])
    async def list_queue(self, ctx: commands.Context):
        try:
            if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
                await ctx.send("佇列為空")
                return

            embed = discord.Embed(title="播放佇列", color=0xadc8ff)
            t = 1
            for item in self.queues[ctx.guild.id]:
                title = item["title"]                
                if t > 25:
                    break
                embed.add_field(name=f"{t}.", value=title, inline=False)
                t += 1
            await ctx.send(embed=embed)
        except Exception as e:
            print(e, ", list_queue")

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        try:
            if ctx.author.voice:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await asyncio.sleep(1)
                    await self.play_next(ctx)
                else:
                    await ctx.send("沒有正在播放的歌曲")
            else:
                await ctx.send("你不在語音頻道中，請先加入一個語音頻道。")
        except Exception as e:
            print(e, ", skip")

    @commands.command(name="remove_from_queue", aliases=["rfq"])
    async def remove_from_queue(self, ctx, index: int):
        try:
            if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
                await ctx.send("佇列中沒有歌曲。")
                return

            if index < 1 or index > len(self.queues[ctx.guild.id]):
                await ctx.send("請提供有效的歌曲索引。")
                return

            removed_song = self.queues[ctx.guild.id].pop(index - 1)
            removed_title = removed_song["title"]
            await ctx.send(f"已從佇列中刪除歌曲：{removed_title}")

        except Exception as e:
            print(e, ", remove_from_queue")

    def url_format(self,url):
        if self.youtube_base_url not in url:
            query_string = urllib.parse.urlencode({'search_query': url})
            content = urllib.request.urlopen(self.youtube_results_url + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
            url = self.youtube_watch_url + search_results[0]

        patterns = [
            r'v=([a-zA-Z0-9_-]{11})',       # Pattern for 'v='
            r'youtu\.be/([a-zA-Z0-9_-]{11})' # Pattern for 'youtu.be/'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                print(f"獲取ID:{match.group(1)}")
                url = self.youtube_watch_url + match.group(1)
                return url
        return url



async def setup(bot: commands.Bot):
    await bot.add_cog(Youtube(bot))