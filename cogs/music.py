import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
import os, imp
import youtube_dl
from youtube_dl import YoutubeDL
import asyncio
import urllib.request
import urllib.parse
import re
import lxml
from lxml import etree
import shutil
from colorama import init, Fore, Back, Style
imp.load_source("general", os.path.join(os.path.dirname(__file__), "../general.py"))
import general as gen
from asyncio import sleep
from threading import Thread


class Music(commands.Cog):
    ''':musical_note: The title says it all, commands related to music and stuff.'''

    queues = []
    loop_song = False
    skip_song = False
    auto_disconnect_time = 300
    is_disconnecting = False
    music_logo = "https://cdn.discordapp.com/attachments/623969275459141652/664923694686142485/vee_tube.png"

    def __init__(self, client):
        self.client = client
        self.skip_song = False
        self.loop_song = False
        self.is_disconnecting = False
        self.disconnecting_signal =False
        self.resume_signal=False
        self.auto_pause.start()

    @tasks.loop(seconds=2)
    async def auto_pause(self):
        self.resume_signal=False
        guild = self.client.get_guild(gen.server_id)
        awoo_channel = self.client.get_channel(gen.awoo_id)

        voice = get(self.client.voice_clients, guild=guild)

        if voice and len(voice.channel.members) <= 1:
            if voice.is_playing():
                self.log("Player AUTO paused")
                voice.pause()
                await awoo_channel.send(f"Everyone left `{voice.channel.name}`, player paused.")
                self.disconnecting_signal=False
                self.auto_resume.start()
            for i in range(300):
                   
                if not self.resume_signal:
                    await asyncio.sleep(1)
                else:
                    break
            else:

                await self.auto_disconnect()
                self.auto_resume.stop()
                
        

    @tasks.loop(seconds=1)
    async def auto_resume(self):
        guild = self.client.get_guild(gen.server_id)
        awoo_channel = self.client.get_channel(gen.awoo_id)

        voice = get(self.client.voice_clients, guild=guild)

        if voice and voice.is_paused() and len(voice.channel.members) > 1:
            self.log("Music AUTO resumed")
            voice.resume()
            await awoo_channel.send(f"Looks like someone joined `{voice.channel.name}`, player resumed.")
            self.resume_signal=True
            self.auto_resume.stop()
       
        
    async def auto_disconnect(self):
    
        guild = self.client.get_guild(gen.server_id)
        voice = get(self.client.voice_clients, guild=guild)
   
       
        awoo_channel = self.client.get_channel(gen.awoo_id)
 
        await voice.disconnect()

        await awoo_channel.send(f"I was left all alone, so I left VC `{voice.channel.name}`")
        self.log(f"Auto disconnected from {voice.channel.name}")
        self.queues.clear()
    
    def log(self, msg):
        cog_name = os.path.basename(__file__)[:-3]
        debug_info = gen.db_receive("var")["cogs"]
        if debug_info[cog_name] == 1:
            return gen.error_message(msg, gen.cog_colours[cog_name])
        
    def player(self,voice):
        def check_queue():
            DIR = os.path.abspath(os.path.realpath("./Queue"))
            length = len(os.listdir(DIR))
            if ((not self.loop_song) or (self.skip_song)):
                os.remove(self.queues[0][1])
                self.queues.pop(0)
                self.skip_song = False

            if length > 0:
                                
                self.log(f"\nSong done, playing {self.queues[0][2]}")
                self.log(f"Songs still in queue: {len(self.queues)}")


                voice.play(discord.FFmpegPCMAudio(self.queues[0][1]),
                               after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.4
            else:
                self.queues.clear()
                #await ctx.send(">>> All songs played. No more songs to play.")   
                self.log("Ending the queue")
                return

        self.log(f"{self.queues[0][2]} is playing.")
        voice.play(discord.FFmpegPCMAudio(self.queues[0][1]),
                    after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.4

    def get_title(self, url: str):
        ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return info.get('title', None)

    def get_thumbnail(self, url: str):
        return "http://img.youtube.com/vi/%s/0.jpg" % url[31:]      
    
    def join_list(self, ls):
        return " ".join(ls)

    def url_get(self,query):
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
        return url

    def download_music(self,url,name,path,mtype):

        queue_path = os.path.abspath(f"{path}/{name}.{mtype}")
        ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'outtmpl': queue_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': mtype,
                }],
            }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                self.log("Downloading stuff now")
                ydl.download([url])
        except :
            pass
        return queue_path

    @commands.command()
    async def join(self, ctx):
        '''Joins the voice channel you are currently in.'''

        try:
            channel = ctx.message.author.voice.channel
        except:
            await ctx.send("You should be in VC dumbo.")
            return False
       
        voice = get(self.client.voice_clients, guild=ctx.guild)
        
        if not voice:
            voice = await channel.connect()
            await ctx.send(f">>> Joined `{channel}`")
            return True
        
        

        elif ctx.author in voice.channel.members:
            return True
        
        elif voice and len(voice.channel.members)==1:
            await voice.move_to(channel)
            await ctx.send(f">>> Joined `{channel}`")
            return True
        
        
        else:
            await ctx.send(f"I am already connected to a voice channel and someone is listening to the songs. Join {voice.channel.name}")
            return False
    @commands.command()
    async def play(self, ctx, *,query):
        '''Plays the audio of the video in the provided YOUTUBE url.'''
  
        if not (await ctx.invoke(self.client.get_command("join"))):
            return
        
        url = self.url_get(query)

        #! Queueing starts here
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        Queue_infile = os.path.isdir(f"{os.getcwd()}/Queue")
        if voice and (not voice.is_playing()):
            try:
                Queue_folder = f"{os.getcwd()}/Queue"
                if Queue_infile:
                    self.log("removed old queue folder")
                    shutil.rmtree(Queue_folder)
            except:
                self.log("No old queue folder")

        if not Queue_infile:
            os.mkdir("Queue")

        q_num = len(self.queues)+1
              
        title =str(self.get_title(url))
        thumbnail =str(self.get_thumbnail(url))
       
        embed = discord.Embed(title="Song Added to Queue",      #TODO make a function
                              url=url, color=discord.Colour.blurple())
        embed.set_author(name="Me!Me!Me!",
                         icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                         icon_url=ctx.message.author.avatar_url)
        embed.add_field(name=f"**#{q_num}**",
                        value=title)
        embed.set_image(url=thumbnail)
        embed.set_thumbnail(url=self.music_logo)
        await ctx.send(embed=embed)
        if self.queues == []:
            l=1
        else:
            l = int(self.queues[-1][1].split("\\")[-1].split(".")[0][4:])+1
      

        self.log("Song added to queue")
        
        path=self.download_music(url,f"song{l}","./Queue","webm")
        self.queues +=[[url,path,title,thumbnail]]
        self.log("Downloaded")

                

        if len(self.queues) == 1:
            thrd = Thread(target=self.player, args=(voice,))
            thrd.start()
            
    @commands.command(aliases=['lp'])
    async def loop(self, ctx,toggle = ""):
        '''Loops the current song, doesn't affect the skip command tho. If on/off not passed it will toggle it.'''

        if toggle.lower() == "on":
            self.loop_song = True
            await ctx.send(">>> **Looping current song now**")

        elif toggle.lower() == 'off':
            self.loop_song = False
            await ctx.send(">>> **NOT Looping current song now**")
                
        else:
            
            if self.loop_song:
                self.loop_song = False
                await ctx.send(">>> **NOT Looping current song now**")
                
            else:
                self.loop_song = True
                await ctx.send(">>> **Looping current song now**")
    
    @commands.command()
    async def restart(self,ctx):
        '''Restarts the current song.'''

        temp = self.loop_song
        self.loop_song = True
        voice = get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()
        await asyncio.sleep(0.1)
        self.loop_song = temp
                
    @commands.group(aliases=['q'])
    async def queue(self, ctx):
        '''Shows the current queue.'''

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="QUEUE",
                             color=discord.Colour.dark_purple())
            embed.set_author(name="Me!Me!Me!",
                                 icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=self.music_logo)
            embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                                 icon_url=ctx.message.author.avatar_url)
            
            for i in range(1,len(self.queues)+1):
                
                embed.add_field(name="** **", value=f"{i}. {self.queues[i-1][2]}",inline=False)
            
            await ctx.send(embed=embed)


    @queue.command(aliases=['move'])
    async def replace(self,ctx,change1,change2):
        '''Replaces two queue members.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        try:
            change1,change2=int(change1),int(change2)
        except:
            await ctx.send("NUMBERS GODDAMN NUMBERS")
            return
            
        if change1 >1 and change2>1 and change1 <= len(self.queues) and change2 <= len(self.queues):
            await ctx.send(f">>> Switched the places of **{self.queues[change2-1][2]}** and **{self.queues[change1-1][2]}**")
            self.queues[change1-1],self.queues[change2-1]=self.queues[change2-1],self.queues[change1-1]
        else:
            await ctx.send("The numbers you entered are just as irrelevant as your existence.")
            return

    @queue.command()
    async def remove(self,ctx,remove):
        '''Removes the Queue member.'''
        
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC.")
            return
        try:
            remove=int(remove)
        except:
            await ctx.send("NUMBERS GODDAMN NUMBERS")
            return
            
        if remove >1 and remove <= len(self.queues):
            os.remove(self.queues[remove-1][1])
            await ctx.send(f">>> Removed **{(self.queues[remove - 1][2])}** from the queue.")
            self.queues.pop(remove-1)
        else:
            await ctx.send("The number you entered is just as irrelevant as your existence.")
            return

    @queue.command()
    async def now(self,ctx,change):
        '''Plays a queue member NOW.'''
        
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        try:
            change=int(change)
        except:
            await ctx.send("NUMBERS GODDAMN NUMBERS")
            return
        if change >1 and change <= len(self.queues):
            temp=self.queues[change-1]
            self.queues.pop(change-1)
            self.queues.insert(1,temp)
        else:
            await ctx.send("The number you entered is just as irrelevant as your existence.")
            return
        await ctx.invoke(self.client.get_command("next"))
        
   
    @commands.command(aliases=['p'])
    async def pause(self, ctx):
        '''Pauses the current music.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        if voice and voice.is_playing():
            self.log("Player paused")
            voice.pause()
            await ctx.send(">>> Music Paused")
        else:
            self.log("Pause failed")
            await ctx.send(">>> Ya know to pause stuff, stuff also needs to be playing first.")

    @commands.command(aliases=['r', 'res'])
    async def resume(self, ctx):
        '''Resumes the current music.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        
        if voice and voice.is_paused():
            self.log("Music resumed")
            voice.resume()
            await ctx.send(">>> Resumed Music")
        else:
            self.log("Resume failed")
            await ctx.send(">>> Ya know to resume stuff, stuff also needs to be paused first.")

    @commands.command(aliases=['st','yamero'])
    async def stop(self, ctx):
        '''Stops the current music AND clears the current queue.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send("You are not even in the VC.")
            return
        
        self.queues.clear()
        

        #! Deleting Queue folder
        Queue_infile = os.listdir("./Queue")
        
        if voice and voice.is_playing:
            self.log("Player stopped")
            voice.stop()
            await ctx.send(">>> Music stopped")
        
        else:
            self.log("Stop failed")
            await ctx.send(">>> Ya know to stop stuff, stuff also needs to be playing first.")

        if Queue_infile:
            shutil.rmtree("./Queue")

        
       

    @commands.command(aliases=['n', 'sk', 'skip'])
    async def next(self, ctx):
        '''Skips the current song and plays the next song in the queue.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send("You are not even in the VC.")
            return
        if voice and voice.is_playing():
            self.skip_song = True
            self.log("Playing next song")
            voice.stop()
            await ctx.send(">>> ***Song skipped.***")
        else:
            self.log("Skip failed")
            await ctx.send(">>> Wat you even trynna skip? There is ***nothing to*** skip, I am surrounded by idiots")

    @commands.command()
    async def leave(self, ctx):
        '''Leaves the voice channel.'''

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send("You are not even in the VC.")
            return
        
        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send(f">>> Left ```{voice.channel.name}```")
            self.queues.clear()

        else:  
            await ctx.send(">>> I cannot leave a voice channel I have not joined, thought wouldn't need to explain basic shit like this.")
            
    @commands.command(aliases=["dnld"])
    async def download(self, ctx, *,query):
        '''Downloads a song for you, so your pirated ass doesn't have to look for it online.'''

        url = self.url_get(query)
        embed = discord.Embed(title="Now downloading",
                              color=discord.Colour.dark_purple(), url=url)
        embed.set_author(name="Me!Me!Me!",
                         icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.music_logo)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                         icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=self.get_thumbnail(url))
        embed.add_field(name="**  **", value=f"**{self.get_title(url)}**")
        
        await ctx.send(embed=embed)
        
        files = os.listdir("./Download")
        if files==[]:
            i=1
        else:
            last_file = files[-1]
            i=int(last_file.split(".")[0][4:])+1
        
                   
        path=self.download_music(url,f"dnld{i}","./Download","webm")
        self.log("Downloaded")
        
                
        mp3 = discord.File(path, filename=self.get_title(url)+".mp3")
        
        await ctx.channel.send(file=mp3)
        os.remove(path)

    


def setup(client):
    client.add_cog(Music(client))
