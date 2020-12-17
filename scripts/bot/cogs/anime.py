import sys
import os

from discord.ext.commands.cooldowns import BucketType
sys.path.append(os.path.abspath("./scripts/others/"))

import discord
import asyncio
from random import choice
from discord.ext import commands
from MAL import Anime as AnimeObject, MALConfig
from dotenv import load_dotenv
load_dotenv()

class Anime(commands.Cog):
      
    config = MALConfig(
    client_id = os.environ.get("MAL_CLIENT_ID"),
    client_secret = os.environ.get("MAL_CLIENT_SECRET"),
    access_token = os.environ.get("MAL_ACCESS_TOKEN"),
    refresh_token = os.environ.get("MAL_REFRESH_TOKEN")
    )
    
    MAL_LOGO = "https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png"
    
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        
    @staticmethod
    def format_list(l) -> str:
        result = ""
        for i, j in enumerate(l):
            if not i == len(l) - 1:
                result += f"`{j}` | "
            else:
                result += f"`{j}`"
                
        return result
        
    @commands.command()
    @commands.cooldown(rate=3, per=4, type=BucketType.member)
    async def anime(self, ctx, *, query):
        result = list(AnimeObject.search(query=query, limit=10, basic=True, config=Anime.config))
        if len(result) == 0:
            await ctx.send(f"No anime of name `{query}` found.")
            return
        
        msg_content = "Respond with the index of the anime you want, 'c' to cancel\n"
        for index, anime in enumerate(result):
            anime_name = anime["name"]
            msg_content += f"{index + 1}. **{anime_name}**\n"
        
        search_message = await ctx.send(msg_content)
        
        def check(message) -> bool:
            return message.author == ctx.author and ((message.content.isdigit() or message.content[1:].isdigit()) or message.content.lower() == "c")
        
        the_chosen_id = None
        errors_commited = 0
        
        while True:
              
            if errors_commited >= 3:
                await search_message.edit(content="Bruh you are too retarded I give up")
                return
                
            try:
                response = await self.client.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("I got no response sadly, try refining your search term if you didn't find your anime.")
                return
            else:
                response_content = response.content.lower()
              
                if response_content == "c":
                    await search_message.edit(content="Command cancelled, try refining your search term if you didn't find your anime.")
                    return
                
                elif int(response_content) <= 0:
                    await ctx.send("Respond with a natural number, should have been obvious enuff.")
                    errors_commited += 1
                    continue
                
                elif int(response_content) > len(result):
                    await ctx.send("I dont even have that many results bro, try again.")
                    errors_commited += 1
                    continue
                
                else:
                    the_chosen_id = result[int(response_content) - 1]["anime_id"]
                    break
                
        found_anime = AnimeObject(the_chosen_id, Anime.config)
        
        embed_1 = discord.Embed(title=f"{found_anime.english_title} `{found_anime.japenese_title}`", url=found_anime.url, color=discord.Colour.red())
        embed_1.set_author(name="Me!Me!Me!", icon_url=self.client.user.avatar_url)
        embed_1.set_thumbnail(url=Anime.MAL_LOGO)
        embed_1.set_image(url=found_anime.cover)
        embed_1.description = found_anime.synopsis + "\n\n" + found_anime.background
        
        embed_2 = discord.Embed(title=f"{found_anime.english_title} `{found_anime.japenese_title}`", url=found_anime.url, color=discord.Colour.red())
        embed_2.set_author(name="Me!Me!Me!", icon_url=self.client.user.avatar_url)
        embed_2.set_thumbnail(url=Anime.MAL_LOGO)
        embed_2.set_image(url=choice(found_anime.pictures))
        
        embed_2.add_field(name="Score", value=f"`{found_anime.score}`")
        embed_2.add_field(name="Rank", value = f"`{found_anime.rank}`")
        embed_2.add_field(name="Popularity", value = f"`{found_anime.popularity}`")
        embed_2.add_field(name="Number of episodes", value = f"`{found_anime.number_of_episodes}`")
        embed_2.add_field(name="Season", value = f"`{found_anime.season}`")
        embed_2.add_field(name="Broadcast", value = f"`{found_anime.broadcast.capitalize()}`")
        embed_2.add_field(name="Release", value = f"`{found_anime.release_date}`")
        embed_2.add_field(name="End", value = f"`{found_anime.end_date}`")  
        embed_2.add_field(name="Status", value = f"`{found_anime.status.capitalize()}`")
        embed_2.add_field(name="Age rating", value = f"`{found_anime.age_rating.upper()}`")                
        embed_2.add_field(name="Genres", value=self.format_list(found_anime.genres))
        embed_2.add_field(name="Studio(s)", value = self.format_list(found_anime.studios))
        
        embed_pages = [embed_1, embed_2]
        current_page = 0
        
        await search_message.edit(content="", embed=embed_1)
        
        async def reactions_add(message, reactions):
            for reaction in reactions:
                await message.add_reaction(reaction)
                
        reactions = {"⬅" : "back", "➡" : "forward"}

        def reaction_check(reaction, user):
            return (not user.bot) and reaction.message.id == search_message.id and str(reaction) in reactions.keys()

        self.client.loop.create_task(reactions_add(search_message, reactions.keys()))
        
        while True:

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=reaction_check)
            except asyncio.TimeoutError:
                await search_message.clear_reactions()
                return
            else:
                reaction_response = reactions[str(reaction)]
                await search_message.remove_reaction(str(reaction.emoji), user)
                
                if reaction_response == "forward":
                    if not current_page == len(embed_pages) - 1:
                        current_page += 1
                    else:
                        current_page = 0
                
                elif reaction_response == "back":
                    if not current_page == 0:
                        current_page -= 1
                    else:
                        current_page = len(embed_pages) - 1
                        
                await search_message.edit(embed=embed_pages[current_page])

def setup(client):
    client.add_cog(Anime(client))