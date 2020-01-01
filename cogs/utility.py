import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime

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
        
        roles = [role for role in member.roles]
        role_names = []
        for role in roles:
            role_names +=[role.mention]
        joined_at = member.joined_at.strftime("%a, %d %B %Y %H:%M:%S UTC")
        created_at = member.created_at.strftime("%a, %d %B %Y %H:%M:%S UTC")
        
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)

        embed.set_author(name=f"User info of {member.name}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="ID: ",value=member.id)
        embed.add_field(name="Guild's Nickname: ",value=member.nick)
      
        embed.add_field(name="Top role: ",value=member.top_role.mention)
        embed.add_field(name=f"Roles ({len(roles)})",value=" | ".join(role_names) ,inline = False)
        embed.add_field(name="Joined at",value=joined_at)
        embed.add_field(name="Created at",value=created_at)
        
        await ctx.send(embed=embed)
    
    #*AVATAR
    @commands.command(aliases = ["av"])
    async def avatar(self,ctx,member: discord.Member ):
        if not member:
            member = ctx.author
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)

        embed.set_author(name=f"Avatar info of {member.name}")
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        
        await ctx.send(embed=embed)


    #* HELP
   
    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            help = discord.Embed(
                colour  = discord.Colour.from_rgb(255,50,150),
                title = "ME! HELP {SUBFIELD}",
                description = "This shows all commands. `PREFIX: ME! , EPIC`  `[]: Aliases` `{}: Optional Arguments` `(): Mandatory Arguments`"
            )
            
            help.add_field(name = ":tools: **UTILITY**", value = 'These commands are of great UTILITY.')
            help.add_field(name = ":moneybag:  **CURRENCY**", value = 'Money Money Money Money !!!')
            help.add_field(name = ":grin:  **FUN**", value = 'These commands will make your day great.')
            help.add_field(name = ":ghost: **IMMORTAL COMMANDS**", value = 'These commands are not for some puny mortals, Only Immortal beings possess these commands.', inline = False)

            help.add_field(name=":spy: **TESTING**",value = 
            "TESTING 1 2 3."
            )
            help.add_field(name=":iphone: **PHONE**",value = 'PHONE SIMULATOR 2019.')

            help.add_field(name = ":robot: **ADMINISTRATIVE**", value = 'Commands we Admins have. HAHAHA')
            await ctx.send(embed = help)
    
    @help.command()
    async def administrator(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":robot: **ADMINISTRATIVE**",
                  description = "Commands we Admins have. HAHAHA"
              )
        help.add_field(name = "`ENABLE`(Extension)", value = 'Enable a set of commands.')
        help.add_field(name = "`DISABLE`(Extension)", value = 'Spank a set of commands.')
        help.add_field(name = "`RELOAD`(Extension)", value = 'Reload a set of commands and hope they work.')
        
        await ctx.send(embed = help)
    @help.command()
    async def phone(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":iphone: **PHONE**",
                  description = "PHONE SIMULATOR 2019."
              )
        help.add_field(name = "`PHONE`", value = 'Shows your Phone.')
        help.add_field(name = "`PHONE COLOUR`(Place) (COLOUR in R G B)", value = "Changes wallpaper and body's colour.")
        help.add_field(name = "`PHONE TYPE`(Type)", value = 'Well you can at least get new phones in this virtual world.')
        
        await ctx.send(embed = help)
    @help.command()
    async def testing(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":spy: **TESTING**",
                  description = "TESTING 123."
              )
        help.add_field(name = "`ROLES`", value = 'Shows all your WORTHLESS roles.')
        await ctx.send(embed = help)

    @help.command()
    async def immortal(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":ghost: **IMMORTAL COMMANDS**",
                  description = "These commands are not for some puny mortals, Only Immortal beings possess these commands."
              )
        help.add_field(name = "`LEVEL` (Member) (Level)", value = 'This is a MEE6 exclusive command, no puny mortal can use this.')
        help.add_field(name = "`ADMIN`", value = 'This is a top secret command, no using this.')
        help.add_field(name = "`STATS`", value = 'Shows stats of all the ACTIVE PEOPLE WHO HAVE NO LIFE.')
        help.add_field(name = "`RECORD_STATS`", value = 'Records stats of all the FUCKING SLAVES OF THIS SERVER.')
        await ctx.send(embed = help)


    #?
    #? FUN
    #?

    @help.command()
    async def fun(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":grin:  **FUN**",
                  description = "These commands will make your day great."
              )
        help.add_field(name = "`DIX` [Penis, Dicc, Peepee, Dick]", value = 'Well, i calculate your peepee with my special MEASURING STICK that goes in ME! ass.')
        help.add_field(name = "`QUES` [8ball, _8ball, Question] (Question)", value = 'I have answers to all your questions in this GOD DAMN WORLD.')
        help.add_field(name = "`MEME` {Subreddit} {Amount} {Type}", value = 'Get some fresh memes, you insolent prick.')
        help.add_field(name = "`EMOJI` [Emo] (Emoji){Amount}", value = 'Returns the emoji or maybe not. ')
        await ctx.send(embed = help)

    #?
    #? UTILITY
    #?

    @help.command()
    async def utility(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":tools: **UTILITY**",
                  description = "These commands are of great UTILITY."
              )
        help.add_field(name = "`HELP` {Subfield}", value = 'Shows this MESSAGE. ')
        help.add_field(name = "`CLEAR` {Amount}", value = 'I can delete the evidence of a bully, no one shall know. ')
        help.add_field(name = "`INFO`", value = 'Lemme tell you about ME!!!')
        help.add_field(name = "`PING`", value = 'It really means nothing, but well it tells the DAMN PING.')
        await ctx.send(embed = help)

    @help.command()
    async def currency(self,ctx):
        help = discord.Embed(
                  colour  = discord.Colour.from_rgb(255,50,150),
                  title = ":moneybag:  **CURRENCY**",
                  description = "Money Money Money Money !!!"
              )
        help.add_field(name = "`BET` (Amount)", value = 'Well, this is the only fun part, BET, hail KAKEGURUI.')
        help.add_field(name = "`BANK`", value = ' When you are broke, cry in front of the GOVT. and get some loan to use in a game which will have no impact on your true irl broke ass.')
        help.add_field(name = "`SOULS`", value = 'Just the balance of your souls. THATS IT.')
        await ctx.send(embed = help)
        
def setup(client):
    client.add_cog(Utility(client))