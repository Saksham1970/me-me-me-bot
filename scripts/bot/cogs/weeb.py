import sys
import os

from discord.ext.commands.cooldowns import BucketType
sys.path.append(os.path.abspath("./scripts/others/"))

import discord
import asyncio
from random import choice
from discord.ext import commands
from MAL import Anime, Manga, MALConfig
from state import State
from dotenv import load_dotenv
load_dotenv()

class Weeb(commands.Cog):
      
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
    
    def vault_add(self, user: discord.User, item):
        st = State(member=user).User
    
        vault = st.anime_watch_list
        
        if item in vault:
            return False
        
        vault.append(item)
                
        st.anime_watch_list = vault
        
        return True
    
    def vault_remove(self, user: discord.User, index: int):
        st = State(member=user).User
        vault = st.anime_watch_list
        index = int(index)
        if len(vault) < int(index - 1):
            return None

        removed = vault.pop(index-1)
        
        st.anime_watch_list = vault
        
        return removed
    
    async def weeb_embed(self, ctx, weeb_abc, type, search_message=None ):
        embed_1 = discord.Embed(title=f"{weeb_abc.english_title} `{weeb_abc.japenese_title}`", url=weeb_abc.url, color=discord.Colour.red())
        embed_1.set_author(name="Me!Me!Me!", icon_url=self.client.user.avatar_url)
        embed_1.set_thumbnail(url=Weeb.MAL_LOGO)
        embed_1.set_image(url=weeb_abc.cover)
        
        description = weeb_abc.synopsis + "\n\n" + weeb_abc.background
        
        if len(description) > 2048:
            embed_1.description = description[:2044] + "..."
        else:
            embed_1.description = description
        
        embed_2 = discord.Embed(title=f"{weeb_abc.english_title} `{weeb_abc.japenese_title}`", url=weeb_abc.url, color=discord.Colour.red())
        embed_2.set_author(name="Me!Me!Me!", icon_url=self.client.user.avatar_url)
        embed_2.set_thumbnail(url=Weeb.MAL_LOGO)
        embed_2.set_image(url=choice(weeb_abc.pictures))
        
        embed_2.add_field(name="Score", value=f"`{weeb_abc.score}`")
        embed_2.add_field(name="Rank", value = f"`{weeb_abc.rank}`")
        embed_2.add_field(name="Popularity", value = f"`{weeb_abc.popularity}`")
        
        if type == "anime":
            embed_2.add_field(name="Number of episodes", value = f"`{weeb_abc.number_of_episodes}`")
            embed_2.add_field(name="Season", value = f"`{weeb_abc.season}`")
            embed_2.add_field(name="Broadcast", value = f"`{weeb_abc.broadcast.capitalize()}`")
            embed_2.add_field(name="Studio(s)", value = self.format_list(weeb_abc.studios))
            embed_2.add_field(name="Age rating", value = f"`{weeb_abc.age_rating.upper()}`")                
        elif type == "manga":
            embed_2.add_field(name="Number of volumes", value = f"`{weeb_abc.number_of_volumes}`")
            embed_2.add_field(name="Number of chapters", value = f"`{weeb_abc.number_of_chapters}`")
            embed_2.add_field(name="Author(s)", value = self.format_list(weeb_abc.authors))
            
        embed_2.add_field(name="Release", value = f"`{weeb_abc.release_date}`")
        embed_2.add_field(name="End", value = f"`{weeb_abc.end_date}`")  
        embed_2.add_field(name="Status", value = f"`{weeb_abc.status.capitalize()}`")
        embed_2.add_field(name="Genres", value=self.format_list(weeb_abc.genres))
        
        embed_pages = [embed_1, embed_2]
        current_page = 0
        
        if search_message is not None:
            await search_message.edit(content="", embed=embed_1)
        else:
            search_message = await ctx.send(embed=embed_1)
        
        async def reactions_add(message, reactions):
            for reaction in reactions:
                await message.add_reaction(reaction)
                
        reactions = {"⬅" : "back", "➡" : "forward", "⭐": "fav"}

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
                        
                    await search_message.edit(embed=embed_pages[current_page])
                
                elif reaction_response == "back":
                    if not current_page == 0:
                        current_page -= 1
                    else:
                        current_page = len(embed_pages) - 1
                        
                    await search_message.edit(embed=embed_pages[current_page])
                        
                elif reaction_response == "fav":
                    if type == "manga":
                        await ctx.send("Watch list is not yet supported for manga, support for mangalist coming soon(not really).")
                        continue
                    
                    successfull = self.vault_add(user, int(weeb_abc.id))
                    if successfull:
                        await ctx.send(f"Added `{str(weeb_abc)}` to the watchlist of **{str(user)}**")
                    else:
                        await ctx.send(f"`{str(weeb_abc)}` is already in the watch list of **{str(user)}**")
                    continue
                
    async def embed_pages(self, _content, ctx: commands.Context, embed_msg: discord.Message, check=None, wait_time=90):

        if type(_content) == str:
            if len(_content) < 2048:
                return

        async def reactions_add(message, reactions):
            for reaction in reactions:
                await message.add_reaction(reaction)

        def default_check(reaction: discord.Reaction, user):
            return user == ctx.author and reaction.message.id == embed_msg.id

        if check is None:
            check = lambda reaction, user: user == ctx.author and reaction.message.id == embed_msg.id

    
        if type(_content) == str:
            content_list = _content.split("\n")
            content = []
            l = ""
            for i in content_list:
                if len(l+i) > 2048:
                    content += [l]
                    l = ""
                l += i
                l += "\n"    
            else:
                content += [l]

        elif type(_content) == list:
            content = _content

        pages = len(content)
        page = 1

        embed: discord.Embed = embed_msg.embeds[0]

        def embed_update(page):
            embed.description = content[page - 1]
            return embed

        await embed_msg.edit(embed=embed_update(page=page))

        reactions = {"back": "⬅", "delete": "❌", "forward": "➡"}

        self.client.loop.create_task(reactions_add(
            reactions=reactions.values(), message=embed_msg))

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=wait_time, check=check)
            except TimeoutError:
                await embed_msg.clear_reactions()

                return

            else:
                response = str(reaction.emoji)

                await embed_msg.remove_reaction(response, ctx.author)

                if response in reactions.values():
                    if response == reactions["forward"]:
                        page += 1
                        if page > pages:
                            page = pages
                    elif response == reactions["back"]:
                        page -= 1
                        if page < 1:
                            page = 1
                    elif response == reactions["delete"]:
                        await embed_msg.delete(delay=3)

                        return

                    await embed_msg.edit(embed=embed_update(page=page))
                        
        
    @commands.command()
    @commands.cooldown(rate=3, per=4, type=BucketType.member)
    async def anime(self, ctx, *, query):
        result = list(Anime.search(query=query, limit=10, basic=True, config=Weeb.config))
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
                    
                    try:
                        await response.delete(delay=3)
                    except discord.Forbidden:
                        pass
                    
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
                    
                    try:
                        await response.delete(delay=3)
                    except discord.Forbidden:
                        pass
                    
                    break
                
        found_anime = Anime(the_chosen_id, Weeb.config)
        await self.weeb_embed(ctx=ctx, search_message=search_message, weeb_abc=found_anime, type="anime")
        
    @commands.command()
    @commands.cooldown(rate=3, per=4, type=BucketType.member)
    async def manga(self, ctx, *, query):
        result = list(Manga.search(query=query, limit=10, basic=True, config=Weeb.config))
        if len(result) == 0:
            await ctx.send(f"No manga of name `{query}` found.")
            return
        
        msg_content = "Respond with the index of the manga you want, 'c' to cancel\n"
        for index, manga in enumerate(result):
            manga_name = manga["name"]
            msg_content += f"{index + 1}. **{manga_name}**\n"
        
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
                    await search_message.edit(content="Command cancelled, try refining your search term if you didn't find your manga.")
                    
                    try:
                        await response.delete(delay=3)
                    except discord.Forbidden:
                        pass
                    
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
                    the_chosen_id = result[int(response_content) - 1]["manga_id"]
                    
                    try:
                        await response.delete(delay=3)
                    except discord.Forbidden:
                        pass
                    
                    break
                
        found_anime = Manga(the_chosen_id, Weeb.config)
        await self.weeb_embed(ctx=ctx, search_message=search_message, weeb_abc=found_anime, type="manga")
        
    @commands.group(name="watch-list", aliases=["wl"])
    async def watch_list(self, ctx: commands.Context):
        """The holy VAULT is where you store all your culture, use subcommands to release it to ur dm and do other stuff."""
         
        if ctx.invoked_subcommand is None:
            user_vault = ctx.States.User.anime_watch_list
            
            if user_vault == {}:
                await ctx.send("Looks like your watch list is empty! Add anime to your watch list by pressing ⭐ on the anime embed")
                return
            
            content = [Anime(item, Weeb.config) for item in user_vault]
            
            embed: discord.Embed = discord.Embed(title=f"{ctx.author.name}'s watch list",
                                                color=discord.Color.from_rgb(255, 9, 119))
            embed.set_thumbnail(url=content[0].cover) 
            embed.set_author(name="Me!Me!Me!",
                            icon_url=self.client.user.avatar_url)
            
            content_str = ""
            for index, item in enumerate(content):
                content_str += f"**{index + 1}.** [{str(item)} `{item.japenese_title}`]({item.url})\n\n"
                
            embed.description = content_str
                
            msg = await ctx.send(embed=embed)
            
            await self.embed_pages(content_str, ctx=ctx, embed_msg=msg)
                    
    @watch_list.command()
    async def release(self, ctx: commands.Context):
        """Send your entire watch list to ur DM"""
            
        user_vault = ctx.States.User.vault      
        content = [Anime(item, Weeb.config) for item in user_vault]
        
        if user_vault == {}:
            await ctx.send("Looks like your watch list is empty! Add anime to your watch list by pressing ⭐ on the anime embed")
            return
        
        await ctx.send(">>> Your whole vault is being sent to your DM.")
        await ctx.author.send(">>> Here's your vault, enjoy!")
        
        for item in content:
            await ctx.author.send(embed=self.weeb_embed(weeb_abc=item, author=ctx.author, typre="anime"))
            
        await ctx.author.send("That's all folks.")
    
    @watch_list.command(aliases=["remove"])
    async def pop(self, ctx: commands.Context, index):
        """Remove item from watch list"""
        
        try:
            i = int(index)
        except:
            await ctx.send(">>> Indexes are supposed to be numbers.")
            return
        
        removed_id = self.vault_remove(ctx.author, index=index)
        removed_name = Anime(removed_id, Weeb.config).english_title
        
        if removed_id is None:
            await ctx.send(">>> The index you entered is bigger than the size of your watch list.")
            return
        
        await ctx.send(f"Removed `{removed_name}` from the watch list of {str(ctx.author)}`s")        

def setup(client):
    client.add_cog(Weeb(client))