import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
import os
import youtube_dl
import asyncio
import urllib.request
import urllib.parse
import re
import lxml
from lxml import etree
import shutil


class Music(commands.Cog):

    queues = {}
    music_logo = "https://www.freepnglogos.com/uploads/apple-music-logo-circle-png-28.png"

    def __init__(self, client):
        self.client = client

    def get_title(self, url: str()):
        youtube = etree.HTML(urllib.request.urlopen(url).read())
        video_title = youtube.xpath("//span[@id='eow-title']/@title")

        return "".join(video_title)

    def get_thumbnail(self, url: str()):
        return "http://img.youtube.com/vi/%s/0.jpg" % url[31:]

    def join_list(self, ls):
        return " ".join(ls)
    

    @commands.command(aliases=['q', 'que'])
    async def queue(self, ctx, *query_arg):
        query = self.join_list(query_arg)
        is_url = query.startswith("https://")

        if not is_url:
            query_string = urllib.parse.urlencode({"search_query": query})
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string)
            search_results = re.findall(
                r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            url = "http://www.youtube.com/watch?v=" + search_results[0]
        else:
            url = query

        #! Queueing starts here
        Queue_infile = os.path.isdir(f"{os.getcwd()}/Queue")
        if not Queue_infile:
            os.mkdir("Queue")

        DIR = os.path.abspath(os.path.realpath("./Queue"))
        q_num = len(os.listdir(DIR)) + 1
        add_queue = True

        while add_queue:
            if q_num in self.queues:
                q_num += 1
            else:
                add_queue = False
                self.queues[q_num] = q_num

        queue_path = os.path.abspath(
            os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': queue_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print("Downloading stuff now\n")
                ydl.download([url])
        except:
            pass
        embed = discord.Embed(title="Song Added to Queue",
                              url=url, color=discord.Colour.blurple())
        embed.set_author(name="Me!Me!Me!",
                         icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                         icon_url=ctx.message.author.avatar_url)
        embed.add_field(name=f"**#{q_num + 1}  **",
                        value=str(self.get_title(url)))
        embed.set_image(url=str(self.get_thumbnail(url)))
        embed.set_thumbnail(url=self.music_logo)
        await ctx.send(embed=embed)

        print("Song added to queue\n")

    @commands.command()
    async def join(self, ctx):
        channel_joined = True
        try:
            channel = ctx.message.author.voice.channel
        except:
            await ctx.send(">>> Cool Me! facts : I am not as smol bren as you.")
            return

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)

        else:
            voice = await channel.connect()

        await voice.disconnect()

        if voice and voice.is_connected():
            await voice.move_to(channel)

        else:
            voice = await channel.connect()

        await ctx.send(f">>> Joined ```{channel}```")

    @commands.command()
    async def play(self, ctx, *query_arg):

        def check_queue():
            Queue_infile = os.path.isdir(f"{os.getcwd()}/Queue")
            if Queue_infile:
                DIR = os.path.abspath(os.path.realpath("./Queue"))
                length = len(os.listdir(DIR))
                still_q = length - 1

                try:
                    first_file = os.listdir(DIR)[0]
                except:
                    print("No more queue song(s)\n")
                    self.queues.clear()
                    return

                main_location = os.path.abspath(".")
                song_path = os.path.abspath(
                    os.path.realpath("Queue") + "\\" + first_file)

                if not length == 0:
                    print("Song done, playing next queue")
                    print(f"Songs still in queue: {still_q}")

                    song_there = os.path.isfile("song.mp3")
                    if song_there:
                        os.remove("song.mp3")

                    shutil.move(song_path, main_location)

                    for file in os.listdir("./"):
                        if file.endswith(".mp3"):
                            os.rename(file, "song.mp3")

                    voice.play(discord.FFmpegPCMAudio("song.mp3"),
                               after=lambda e: check_queue())
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.6
                else:
                    self.queues.clear()
                    return

            else:
                self.queues.clear()
                print("No songs queued before the ending of the last song\n")

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if not(voice and voice.is_connected()):
            await ctx.invoke(self.client.get_command("join"))

        query = self.join_list(query_arg)
        is_url = query.startswith("https://")

        if not is_url:
            query_string = urllib.parse.urlencode({"search_query": query})
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string)
            search_results = re.findall(
                r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            url = "http://www.youtube.com/watch?v=" + search_results[0]
        else:
            url = query

        song_there = os.path.isfile("song.mp3")

        try:
            if song_there:
                os.remove("song.mp3")
                self.queues.clear()

        except PermissionError:
            await ctx.send(">>> Wait for the current playing music end or use the 'stop' command")
            return

        Queue_infile = os.path.isdir(f"{os.getcwd()}/Queue")
        try:
            Queue_folder = f"{os.getcwd()}/Queue"
            if Queue_infile:
                print("removed old queue folder")
                shutil.rmtree(Queue_folder)
        except:
            print("No old queue folder")

        await ctx.send(">>> Getting everything ready, playing audio soon")

        voice = get(self.client.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print("Downloading stuff now\n")
                ydl.download([url])
        except:
            pass
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, 'song.mp3')

        embed = discord.Embed(title="Now playing",
                              color=discord.Colour.magenta(), url = url)
        embed.set_author(name="Me!Me!Me!",
                         icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.music_logo)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                         icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=self.get_thumbnail(url))
        embed.add_field(name="**  **", value=f"**{self.get_title(url)}**")
        await ctx.send(embed=embed)

        voice.play(discord.FFmpegPCMAudio("song.mp3"),
                   after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.6

    @commands.command(aliases=['p'])
    async def pause(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing:
            print("Player paused")
            voice.pause()
            await ctx.send(">>> Music Paused")
        else:
            print("Pause failed")
            await ctx.send(">>> Ya know to pause stuff, stuff also needs to be playing first.")

    @commands.command(aliases=['r', 'res'])
    async def resume(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            print("Music resumed")
            voice.resume()
            await ctx.send(">>> Resumed Music")
        else:
            print("Resume failed")
            await ctx.send(">>> Ya know to resume stuff, stuff also needs to be paused first.")

    @commands.command(aliases=['st'])
    async def stop(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        self.queues.clear()

        #! Deleting Queue folder
        Queue_infile = os.listdir("./Queue")
        if Queue_infile:
            shutil.rmtree("./Queue")

        if voice and voice.is_playing:
            print("Player stopped")
            voice.stop()
            await ctx.send(">>> Music stopped")
        else:
            print("Stop failed")
            await ctx.send(">>> Ya know to stop stuff, stuff also needs to be playing first.")

    @commands.command(aliases=['n', 'sk', 'skip'])
    async def next(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing:
            print("Playing next song")
            voice.stop()
            await ctx.send(">>> ***Song skipped.***")
        else:
            print("Skip failed")
            await ctx.send(">>> Wat you even trynna skip? There is ***nothing to*** skip, I am surrounded by idiots")

    @commands.command()
    async def leave(self, ctx):
        try:
            channel = ctx.message.author.voice.channel
        except:
            await ctx.send(
                ">>> You can only make me leave a voice channel if you are in that very voice channel, complex shit, I know.")

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send(f">>> Left ```{channel}```")

        else:
            await ctx.send(">>> I cannot leave a voice channel I have not joined, thought wouldn't need to explain basic shit like this.")


def setup(client):
    client.add_cog(Music(client))
