import discord
import random
import json
from discord.ext import commands
import imp,os
imp.load_source("general", os.path.join(os.path.dirname(__file__), "../general.py"))
import general as gen


class Currency(commands.Cog):

    def __init__(self, client):
        self.client = client      

    #! BET
    @commands.command()
    async def bet(self, ctx, amount : int):
        name = ctx.author.name
        disc = ctx.author.discriminator
        #! GET COINS
        mem_info = gen.db_receive("inf")
        if disc in mem_info:                   
            coins = (mem_info[disc])["coins"]
        else:                                                                                                                        #! TODO MAKE THIS A FUNCTIOn
            gen.new_entry(name,disc)
            coins = (mem_info[disc])["coins"]

        #! REAL BITCH ASS CODE
        if amount <= coins and amount>0:
            player_dye = random.randint(1,6)
            cpu_dye = random.randint(1,6)
            if player_dye > cpu_dye:
                won_lost = "Bet Won"
                amount_rec = (amount)*(player_dye-cpu_dye)
            elif player_dye==cpu_dye:
                won_lost = "Bet Won"
                amount_rec=(amount)*10
            else:
                won_lost = "Bet Lost"
                amount_rec= -(amount)*(cpu_dye-player_dye)
            coins+=amount_rec

            (mem_info[disc])["coins"] = coins
        elif amount<= 0:
            await ctx.send(f">>> So you want a spanky {name}.")
        else:
            await ctx.send(">>> Not enough SOULS man, go hunt.")

        #! EMBED
        if won_lost == "Bet Won":
            colour = discord.Colour.green()

        else:
            colour = discord.Colour.from_rgb(255,0,0)
        bet_list = discord.Embed(
            title = "ME! BET RESULT",
            description = "Lets begin the betting of your souls then.",
            colour = colour
        )

        bet_list.add_field(name="Souls Bet", value =amount ,inline=False)
        bet_list.add_field(name="Your Roll", value = player_dye,inline = True)
        bet_list.add_field(name="ME! Roll", value = cpu_dye,inline = True)
        bet_list.add_field(name = "WON/LOST",value =won_lost ,inline=True)
        bet_list.add_field(name = "Amount Recieved",value = amount_rec,inline=True)
        bet_list.add_field(name = "Total Souls Left",value = coins ,inline=True)
        bet_list.set_author(name = f"{name}'s BET", icon_url = ctx.author.avatar_url)

        await ctx.send(embed = bet_list)
        #! SAVE THOSE DAMN COINS

        gen.db_update("inf",mem_info)

    @bet.error
    async def ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> You need to bet something to gamble, seems like common sense tbh.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(">>> U need to have actual souls, go hunt POET.")
    #BANK
    @commands.command()
    async def bank(self, ctx):
        name = ctx.author.name
        disc = ctx.author.discriminator
        a = random.randrange(1,10)

        mem_info=gen.db_receive("inf")     

        if disc in mem_info:
            coins = (mem_info[disc])["coins"]
        else:
            gen.new_entry(name,disc)                                  
            coins = (mem_info[disc])["coins"]

        if coins == 0:
            (mem_info[disc])["coins"] = a
            await ctx.send(f">>> Given {a} SOULS to {name} get rekt.")
        else:
            await ctx.send(">>> You are way too rich for us, get lost.") 

        gen.db_update("inf",mem_info)

    #SOULS
    @commands.command(aliases=['bal','coins'])
    async def souls(self, ctx):
        name = ctx.author.name
        disc = ctx.author.discriminator 
        
        mem_info=gen.db_receive("inf")

        if disc in mem_info:
            coins = (mem_info[disc])["coins"]
        else:
            mem_info[disc] = {"name": name, "messages" : 0 , "level" : "Prostitute" , "coins" : 500}                                         #! REPLACE
            coins = (mem_info[disc])["coins"]
        await ctx.send(f">>> Souls of {name}: {coins}.")
      
        gen.db_update("inf",mem_info)


def setup(client):
    client.add_cog(Currency(client))