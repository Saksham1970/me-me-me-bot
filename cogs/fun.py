import discord
import random
import general as gen
from discord.ext import commands
import pytesseract
import requests
from PIL import Image
import io

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client 

    

    #! QUES
    @commands.command(aliases=['8ball', '_8ball', 'question'])
    async def ques(self, ctx, *, question):
        responses = [
            'Bilkul.', 'Arey haan.', 'Without a doubt.', 'Definitely.',
            'Aditya Giri says so.', 'Sahi baat.', 'My Boyas says so.',
            'Very well.', 'Yes.', 'My compass point to yes.',
            'Dimaag kharab, no jawaab.', "Can't answer right now.",
            'Kya tha? Bhul gyi.', 'Prediction.exe stopped working.',
            'Meditation.exe started.', "Nikal Laude. Galat h.", 'Nahi.',
            'Aditya Giri said no.', 'Bhag bhosadike. No.', 'What the fuck.'
        ]

        que = discord.Embed(
            title = "ME! ANSWER QUESTION",
            colour = discord.Colour.blue(),
            description = "I will answer your GOD DAMN question, So here it is."
        )
        que.add_field(name = "Question",value= question)
        que.add_field(name = "Answer",value = random.choice(responses))

        await ctx.send(embed = que)
    @ques.error
    async def ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> Enter the question boss.")

    #! DIX
    @commands.command(aliases=['penis', 'dicc', 'peepee', 'dick'])
    async def dix(self, ctx):
        random_p = random.randrange(1, 10)
        dicc_string = random_p 
        name = str(ctx.message.author)[:-5]
      
        for role in ctx.author.roles:
            if role.id == gen.admin_role_id:
                dicc_string = 11
        dix = discord.Embed(
            title = "ME! DIX MACHINE",
            colour = discord.Colour.from_rgb(255,255,255),
            description = f"{name}'s peepee is 8{'='*dicc_string}D long. \n You are a truly disgusting creature, asking ME! for sizes of dicks"
        )

        await ctx.send(embed = dix)
  
    #! EMOJI
    @commands.command(aliases = ['emo'])
    async def emoji(self,ctx,emoji_name,amount = 3):
      strs = f":{emoji_name}: "*amount
      await ctx.send(strs)
    @emoji.error
    async def emoji_error(self,ctx,error):
      await ctx.send(">>> Are you an emoji? Perhaps.")


    #! OCR
    @commands.command()
    async def ocr(self,ctx,im = ""):
        if im =="":
            await ctx.send("Enter a url.")
            return
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
       
        embed = discord.Embed(colour=discord.Colour.green(), timestamp=ctx.message.created_at)

        response = requests.get(im)
        img = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(img, lang="eng")

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_image(url=im)
        embed.add_field(name='Text',value=text)
        await ctx.channel.purge(limit=2)
        await ctx.send(embed=embed)
        

def setup(client):
    client.add_cog(Fun(client))
