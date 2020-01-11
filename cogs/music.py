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

    queues = []
    music_logo = "https://cdn.discordapp.com/attachments/623969275459141652/664923694686142485/vee_tube.png"

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

        queue_path = os.path.abspath(f"{path}/{name}.%(ext)s")
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
                print("Downloading stuff now\n")
                ydl.download([url])
        except:
            pass

    @commands.command()
    async def join(self, ctx):
        
        try:
            channel = ctx.message.author.voice.channel
        except:
            pass
       
        voice = get(self.client.voice_clients, guild=ctx.guild)
       
        if not voice:
            voice = await channel.connect()
            await ctx.send(f">>> Joined ```{channel}```")
        elif voice and len(voice.channel.members)==1:
            await voice.move_to(channel)
            await ctx.send(f">>> Joined ```{channel}```")
        
        elif ctx.author not in voice.channel.members:
            await ctx.send("I am already connected to a voice channel and someone is listening to the songs. Join {voice.channel.name}")
        
    @commands.command()
    async def play(self, ctx, *,query):

        def check_queue():
            DIR = os.path.abspath(os.path.realpath("./Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            if length > 1:

                
                first_file = os.listdir(DIR)[0]
                now = int(first_file[:-5][4:])
                mnext = now+1
                print(now)
                os.remove("./Queue/" + f"song{now}.webm")
                self.queues.pop(0)
                
                print("Song done, playing next queue \n")
                print(f"Songs still in queue: {still_q}")


                voice.play(discord.FFmpegPCMAudio(f".\Queue\song{mnext}.webm"),
                               after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.4
            else:
                self.queues.clear()
                #await ctx.send("All songs played. No more songs to play.")   * PLEASE DO SOMETHING ABOUT THIS
                print("Ending the queue")
                return

            
       
  
        await ctx.invoke(self.client.get_command("join"))
        
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
                    print("removed old queue folder")
                    shutil.rmtree(Queue_folder)
            except:
                print("No old queue folder")

        if not Queue_infile:
            os.mkdir("Queue")

        q_num = len(self.queues)+1
              

       
        embed = discord.Embed(title="Song Added to Queue",      #TODO make a function
                              url=url, color=discord.Colour.blurple())
        embed.set_author(name="Me!Me!Me!",
                         icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                         icon_url=ctx.message.author.avatar_url)
        embed.add_field(name=f"**#{q_num}**",
                        value=str(self.get_title(url)))
        embed.set_image(url=str(self.pget_thumbnail(url)))
        embed.set_thumbnail(url=self.music_logo)
        await ctx.send(embed=embed)

        
        self.queues+= [self.get_title(url)]

        print("Song added to queue\n")
        l = len(self.queues)
        self.download_music(url,f"song{l}","./Queue","webm")

        print("Downloaded")

        DIR = os.path.abspath(os.path.realpath("./Queue"))
        first_file = os.listdir(DIR)[0]
        
        

        if voice and (not voice.is_playing()):
            print(first_file,"is playing.")
            voice.play(discord.FFmpegPCMAudio(f"./Queue/{first_file}"),
                    after=lambda e: check_queue())
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.4
            
    @commands.group(aliases=['q'])
    async def queue(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="QUEUE",
                             color=discord.Colour.dark_purple())
            embed.set_author(name="Me!Me!Me!",
                                 icon_url=self.client.user.avatar_url)
            embed.set_thumbnail(url=self.music_logo)
            embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}",
                                 icon_url=ctx.message.author.avatar_url)
            
            for i in range(1,len(self.queues)+1):
                
                embed.add_field(name="** **", value=f"{i}. {self.queues[i-1]}",inline=False)
            
            await ctx.send(embed=embed)


    @queue.command(aliases=['move'])
    async def replace(self,ctx,change1,change2):
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
            self.queues[change1-1],self.queues[change2-1]=self.queues[change2-1],self.queues[change1-1]
            await ctx.send("DONE BOSS")
        else:
            await ctx.send("Enter Numbers greater than 1.")
            return
    @queue.command()
    async def remove(self,ctx,remove):
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
            self.queues.pop(remove-1)
            await ctx.send("DONE BOSS")
        else:
            await ctx.send("Enter Numbers greater than 1.")
            return
    @queue.command()
    async def now(self,ctx,change):
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
            await ctx.send("Enter Numbers greater than 1.")
            return
        await ctx.invoke(self.client.get_command("next"))
        
   
    @commands.command(aliases=['p'])
    async def pause(self, ctx):
        
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        if voice and voice.is_playing():
            print("Player paused")
            voice.pause()
            await ctx.send(">>> Music Paused")
        else:
            print("Pause failed")
            await ctx.send(">>> Ya know to pause stuff, stuff also needs to be playing first.")

    @commands.command(aliases=['r', 'res'])
    async def resume(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send(f"You are not even in the VC. Join {voice.channel.name}")
            return
        
        if voice and voice.is_paused():
            print("Music resumed")
            voice.resume()
            await ctx.send(">>> Resumed Music")
        else:
            print("Resume failed")
            await ctx.send(">>> Ya know to resume stuff, stuff also needs to be paused first.")

    @commands.command(aliases=['st','yamero'])
    async def stop(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send("You are not even in the VC.")
            return
        
        self.queues.clear()
        

        #! Deleting Queue folder
        Queue_infile = os.listdir("./Queue")
        
        if voice and voice.is_playing:
            print("Player stopped")
            voice.stop()
            await ctx.send(">>> Music stopped")
        
        else:
            print("Stop failed")
            await ctx.send(">>> Ya know to stop stuff, stuff also needs to be playing first.")

        if Queue_infile:
            shutil.rmtree("./Queue")

        
       

    @commands.command(aliases=['n', 'sk', 'skip'])
    async def next(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if ctx.author not in voice.channel.members:
            await ctx.send("You are not even in the VC.")
            return
        if voice and voice.is_playing():
            print("Playing next song")
            voice.stop()
            await ctx.send(">>> ***Song skipped.***")
        else:
            print("Skip failed")
            await ctx.send(">>> Wat you even trynna skip? There is ***nothing to*** skip, I am surrounded by idiots")

    @commands.command()
    async def leave(self, ctx):
        
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
            i=int(last_file[:-6][4:])+1
        
                   
        self.download_music(url,f"dnld{i}","./Download","webm")
        print("Downloaded")
        
                
        mp3 = discord.File(f"./Download/dnld{i}.webm", filename=self.get_title(url)+".mp3")
        
        await ctx.channel.send(file=mp3)
        os.remove(f"./Download/dnld{i}.webm")


def setup(client):
    client.add_cog(Music(client))
