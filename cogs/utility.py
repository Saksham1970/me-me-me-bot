import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime
import imp, os
imp.load_source("general", os.path.join(os.path.dirname(__file__), "../general.py"))
import general as gen

#! RECALLING FUNCTIONS
def check_command(ctx,member):
    roles = [role for role in member.roles]
    role_names = []
    for role in roles:
        role_names +=[role.mention]
    joined_at = member.joined_at.strftime("%a, %d %B %Y %H:%M:%S UTC")
    created_at = member.created_at.strftime("%a, %d %B %Y %H:%M:%S UTC")
    
    embed = discord.Embed(colour=member.colour, 
                          title = f"User info of {member.name}",
                          url = str(member.avatar_url),
                          timestamp=ctx.message.created_at)



    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.add_field(name="ID: ",value=member.id)
    embed.add_field(name="Guild's Nickname: ",value=member.nick)
    
    embed.add_field(name="Top role: ",value=member.top_role.mention)
    embed.add_field(name=f"Roles ({len(roles)})",value=" | ".join(role_names) ,inline = False)
    embed.add_field(name="Joined at",value=joined_at)
    embed.add_field(name="Created at",value=created_at)
    
    return embed

def avatar_command(ctx,member):
    embed = discord.Embed(colour=member.colour, 
                          title = f"Avatar info of {member.name}",
                          url = str(member.avatar_url),
                          timestamp=ctx.message.created_at)

    

    embed.set_image(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    
    return embed
class Utility(commands.Cog):

    def __init__(self, client):
        self.client = client

    #* PING
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f">>> ME! PING: `{round(self.client.latency* 1000)}ms` ")

    #* INFO 
    @commands.command()
    async def info(self, ctx):
        info = discord.Embed(
            colour = discord.Colour.red(),
            title = "ME!ME!ME!",
            description = """Hello, I am sex-slave owned by **Saksy-sama** and the epicest man alive **Blonteractor**.
            `I feel horny.
            I wanna ride on your ugly bastard ass.
            Oh Yes Daddy, Slap me like every ratchet whores from A bad neighbourhood.`
            """
            )
        await ctx.send(embed = info)
        await ctx.send(">>> `Watch my favourite music video:` https://youtu.be/rkBCfF3vUNk")

    #* CLEAR
    @commands.command()
    async def clear(self, ctx, amount=10):
        if amount>0:
            await ctx.channel.purge(limit=amount+1)
            await ctx.send(f">>> {amount} messages deleted boss. Now no one will know you were bullied")
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=1)
        else:
            ctx.send('>>>REALLY? no wait Really? Are You Dumb or something?')

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> Enter the amount of mesages to be cleared if you dont want spanky / or do (depending on who you are)")

    #* SUGGEST
    @commands.command()
    async def suggest(self,ctx,*,suggestion):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            colour = discord.Colour.from_rgb(255,0,0),
            title = "Suggestion",
            
            description = suggestion

        )
        embed.set_author(name =ctx.author.name,icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)
   
    #*Check
       
    @commands.command(aliases = ["about"])
    async def check(self,ctx, member: discord.Member):
        embed = check_command(ctx,member)
        await ctx.send(embed=embed) 
       
    @check.error
    async def check_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            member =  ctx.author
            embed = check_command(ctx,member)
            await ctx.send(embed=embed) 
            
    #*AVATAR    
    
    @commands.command(aliases = ["av"])
    async def avatar(self,ctx,member: discord.Member ):
        await ctx.send(embed=avatar_command(ctx,member))
        
    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            member =  ctx.author
            await ctx.send(embed=avatar_command(ctx,member))


    #* HELP
   
    @commands.command()
    async def help(self, ctx, subfield=""):
        
        commands_info = gen.db_receive("commands")
        commands_info: dict()
        inline_threshold = 45
        
        
        if subfield == "":
            
            help = discord.Embed(
                colour  = discord.Colour.from_rgb(255,50,150),
                title = "ME! HELP {SUBFIELD}",
                description = "This shows all commands. `PREFIX: ME! , EPIC`  `[]: Aliases` `{}: Optional Arguments` `(): Mandatory Arguments`"
            )
            
            for info in commands_info:
                emoji = commands_info[info]["emoji"]
                name = commands_info[info]["name"]
                
                
                help.add_field(name = f"{emoji} **{name}**", value = f'>>> `ME! HELP {info.upper()}`')
            
        else:  
            if subfield in commands_info:
                subfield_info = commands_info[subfield]
                subfield_info: dict()
            
            else:
                await ctx.send(">>> That set of commands doesn't even exist.")
                return
            
            emoji = subfield_info["emoji"]
            name = subfield_info["name"]
            desc = subfield_info["description"]
            
            inline_threshold = 60
           
            help = discord.Embed(
                colour  = discord.Colour.from_rgb(255,50,150),
                title = f"{emoji} **{name}**",
                description = f"{desc}")

            for field in subfield_info["fields"].values(): 
                if len(desc) < inline_threshold:
                    help.add_field(name = field["name"], value =field["value"])
                else:
                    help.add_field(name = field["name"], value =field["value"], inline = False)
                
        await ctx.send(embed = help)
        
def setup(client):
    client.add_cog(Utility(client))