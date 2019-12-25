import discord
from discord.ext import commands

class Testing(commands.Cog):

    def __init__(self, client):
        self.client = client  
    
    @commands.command()
    async def roles(self,ctx):
        await ctx.send(ctx.author.roles)
    


def setup(client):
    client.add_cog(Testing(client))