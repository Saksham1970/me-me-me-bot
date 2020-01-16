import discord
from discord.ext import commands

class Testing(commands.Cog):

    def __init__(self, client):
        self.client = client  
    
    @commands.command()
    async def roles(self,ctx):
        await ctx.send(ctx.author.roles)
    @commands.command()
    async def role_rgb(self,ctx,role:discord.Role):
        await ctx.send(role.color.to_rgb())

def setup(client):
    client.add_cog(Testing(client))
