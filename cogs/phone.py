import discord,time
import general as gen
from PIL import Image,ImageDraw,ImageFont
from discord.ext import commands

class Phone(commands.Cog):

    def __init__(self, client):
        self.client = client  
    
    @commands.group()
    async def phone(self,ctx):
        
        
        
        if ctx.invoked_subcommand is None:
            phone_db = gen.db_receive("phone")        
            phones = gen.db_receive("phone_types")  
            if (ctx.author.discriminator) not in phone_db.keys(): 
                phone_db[ctx.author.discriminator] = {"bg_colour":[0,250,250,255],"type":"Pinapple X=Y","body_colour":[0,0,0,255]}
                await ctx.send("Your Phone has been created")
                gen.db_update("phone",phone_db)

            Ptype = phone_db[ctx.author.discriminator]["type"]


            bg_color = tuple(phone_db[ctx.author.discriminator]["bg_colour"])
            body_color = tuple(phone_db[ctx.author.discriminator]["body_colour"])
            bg_pos = tuple(phones[Ptype]["screen"])
            body_pos = tuple(phones[Ptype]["body"])
          
            with Image.open(f"./Phones/{Ptype}.png") as image:
                
                ImageDraw.floodfill(image,xy = bg_pos,value = bg_color)
                ImageDraw.floodfill(image,xy = body_pos,value = body_color)
                                
                image.save('phone.png') 
                
            
            phone = discord.File("phone.png")    
            await ctx.channel.send(file=phone)

    @phone.command()
    async def colour(self,ctx,place,r:int,g:int,b:int):
      
        if r>255 or g>255 or b>255 or r<0 or g<0 or b<0:
            await ctx.send("SHUT UP")
            return
        phone_db = gen.db_receive("phone")
        
        if place == "wallpaper":
            phone_db[ctx.author.discriminator]["bg_colour"]=[r,g,b,255]
        elif place == "body":
            phone_db[ctx.author.discriminator]["body_colour"] =[r,g,b,255]
        else:
            await ctx.send("Wrong Place.")
            return
        
        gen.db_update("phone",phone_db) 
        await ctx.send("DONE BOSS")

    @phone.command()
    async def type(self,ctx,*,Ptype = None):
        phone_db = gen.db_receive("phone")
        phones = gen.db_receive("phone_types")
        if Ptype in phones.keys():
            phone_db[ctx.author.discriminator]["type"]=Ptype
            await ctx.send("DONE BOSS")
        else:
            send_string = '```Please choose out of the following:\n'
            for i in phones:
                send_string += f"-> {i} \n"
            send_string+="```"
            await ctx.send(send_string)

        gen.db_update("phone",phone_db)   
def setup(client):
    client.add_cog(Phone(client))