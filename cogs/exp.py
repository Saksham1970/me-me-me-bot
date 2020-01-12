import discord
from random import randint
from discord.ext import commands, tasks
import imp,os
imp.load_source("general", os.path.join(os.path.dirname(__file__), "../general.py"))
import general as gen

class exp(commands.Cog):
    
    exp_info = {}
    
    def __init__(self, client):
        self.client = client

        self.give_exp.start()
        
    def gen_xp(self):
        return randint(10, 50)

    @tasks.loop(seconds=45)
    async def give_exp(self):
        for member in self.exp_info.values():
            if member["active"]:
                member["xp"] += self.gen_xp()
                member["active"] = False
                
        gen.db_update("exp", self.exp_info)

    def user_entry(self, user: discord.Member):
        member_info = {}
        member_info["id"] = user.id
        member_info["name"] = user.display_name
        member_info["xp"] = 0
        member_info["level"] = 1
        member_info["rank"] = "Prostitute"

        self.exp_info[user.name] = member_info
        gen.db_update("exp", self.exp_info)

        return member_info

         
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.exp_info = gen.db_receive("exp")
        
        if not message.author.bot:
            if message.author.name not in self.exp_info.keys() and not message.author.bot:
                member_info = self.user_entry(message.author)
            
            else:
                member_info = self.exp_info[message.author.name]

            member_info["active"] = True

            self.exp_info[message.author.name] = member_info
          
        gen.db_update("exp", self.exp_info)

    @commands.command(aliases=['xp', 'rank'])
    async def exp(self,ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        data = gen.db_receive("exp")
        
        if user.name in data.keys():
            user_info = gen.db_receive("exp")[user.name]
        else:
            user_info = self.user_entry(user)

        xp = user_info["xp"]
        lvl = user_info["level"]
        rank = user_info["rank"]

        embed = discord.Embed(title="User Info", color=discord.Colour.dark_gold())
        embed.set_author(name="Me!Me!Me!", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested By: {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)
        embed.add_field(name="Level", value=lvl)
        embed.add_field(name="XP", value=xp)
        embed.add_field(name="Designation", value=rank, inline=False)
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)
        


def setup(client):
    client.add_cog(exp(client))
