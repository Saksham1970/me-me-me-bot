import discord
from random import randint
from discord.ext import commands, tasks
import imp,os
imp.load_source("general", os.path.join(os.path.dirname(__file__), "../general.py"))
import general as gen
import requests
import io
from threading import Thread
from PIL import Image,ImageDraw,ImageOps,ImageFont

class exp(commands.Cog):
    
    roles = {"Prostitute":[0,[230, 126, 34]],"Rookie":[5,[153, 45, 34]],"Adventurer":[10,[173, 20, 87]],"Player":[25,[241, 196, 15]],"Hero":[50,[46, 204, 113]],"Council of Numericon":[85,[0, 255, 240]]}
    
    def __init__(self, client):
        self.client = client
        self.exp_info = gen.db_receive('exp')
        self.give_exp.start()
    
    def cog_unload(self):
        self.give_exp.cancel()
        
    def gen_xp(self):
        return randint(15, 25)

    @tasks.loop(minutes =1)
    async def give_exp(self):
    
        for member in self.exp_info:
            
            if self.exp_info[member]["active"]:
                self.exp_info[member]["xp"] += self.gen_xp()
                self.exp_info[member]["active"] = False

                self.exp_info[member]["rel_bar"] = 5 * (self.exp_info[member]["level"] ** 2) + 50 * self.exp_info[member]["level"] + 100 
                self.exp_info[member]["rel_xp"] += self.gen_xp()

                if self.exp_info[member]["rel_xp"] >= self.exp_info[member]["rel_bar"]:
                    self.exp_info[member]["rel_xp"] -= self.exp_info[member]["rel_bar"]
                    self.exp_info[member]["level"] += 1
                    channel = self.client.get_channel(629718364511797259)
                    send = f'Congrats {self.exp_info[member]["name"]}, now you are of level {self.exp_info[member]["level"]} :middle_finger: .'
                    await channel.send(send)
            
                temp = self.exp_info[member]["role"]
                self.exp_info[member]["role"]=self.get_designation(self.exp_info[member]["level"])
                
                if temp != self.exp_info[member]["role"]:
                    channel = self.client.get_channel(629718364511797259)
                    send = f'Congrats {self.exp_info[member]["name"]}, now you are {self.exp_info[member]["role"]} :middle_finger: .'
                    await channel.send(send)
                 
        xplist=[]
        for i in self.exp_info:
            xplist+=[[self.exp_info[i]["xp"],i]]
       
        xplist = sorted(xplist, key=lambda x: x[0])
        for i in range(len(xplist)):
            self.exp_info[xplist[i][1]]["rank"]= len(xplist) - i
            


        gen.db_update("exp", self.exp_info)
 
    def rank_creation(self, ctx , member):

        try:
            mem_info = self.exp_info[str(member.id)]
        except:
            mem_info= self.user_entry(member)
        level = mem_info["level"]
        rank = mem_info["rank"]
        response = requests.get(member.avatar_url)
        avatar_photo = Image.open(io.BytesIO(response.content))
    
        size = (600,600)
        avatar_photo = avatar_photo.resize(size)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + size, fill=255)

        avatar_photo = ImageOps.fit(avatar_photo, mask.size, centering=(0.5, 0.5))
        avatar_photo.putalpha(mask)

        percent = mem_info["rel_xp"]/mem_info["rel_bar"]
        arc_length = percent*(360)
        if arc_length>360:
            arc_length=360
        arc_start = -90
        arc_end = arc_length-90

        a = list(self.roles.keys())
    
        for i in range(len(a)):
            if level<self.roles[a[i]][0]:
                role = a[i-1]
                role_cap,role_colour = self.roles[a[i-1]]
                role_colour = role_colour[:]
                role_next,role_next_colour = self.roles[a[i]]
                break
        else:
            role = "Council of Numericon"
            role_cap = 85
            role_colour = [0, 255, 240]
            role_next_colour = [0,255,240]
            role_next = level
        role_percent = (level - role_cap)/(role_next - role_cap)
    
        for i in range(3):
        
            colour_diff = int((role_next_colour[i] - role_colour[i])*role_percent)
            role_colour[i] += colour_diff
        role_colour = tuple(role_colour)
    

        bg = Image.new("RGB",(1000,1000),color = role_colour )
        fg = Image.new("RGB",(1000,980),color = (0,0,0))
        bg.paste(fg,(0,0))
        bg.paste(avatar_photo,(200,100),avatar_photo)
        
        draw = ImageDraw.Draw(bg)
        draw.arc([(190,90),(810,710)],start = arc_start,end = arc_end,fill =role_colour ,width =10)


        name = member.name
        if len(name)>15:
            name = name[:15]    
        discrim = member.discriminator
        nanotech = ImageFont.truetype("NanoTech Regular.otf", 100)
        roboto_cond = ImageFont.truetype("RobotoCondensed-Light.ttf", 60)
        d =nanotech.getsize(name)[0]
    
        draw.text((50,750),name,font=nanotech)
        draw.text((70+d,750),f"#{discrim}",font=roboto_cond )

        roboto_black = ImageFont.truetype("Roboto-Black.ttf", 110)

        d = roboto_cond.getsize("LEVEL")[0]
        draw.text((600,850),"LEVEL",font = roboto_cond,fill = role_colour)
        draw.text((620+d,810),str(level),font = roboto_black,fill = role_colour)

        d = roboto_cond.getsize("RANK")[0]
        draw.text((50,50),"RANK",font = roboto_cond)
        draw.text((70+d,10),str(rank),font = roboto_black)

        if role == "Council of Numericon":
            role = role.upper()
            x=10
            for i in range(11,20):
                draw.text((950,x),role[i],font = roboto_cond,fill = role_colour)
                x+= roboto_cond.getsize(role[i])[0]+40
        else:
            x = 10
            for i in role.upper():
                draw.text((950,x),i,font = roboto_cond,fill = role_colour)
                x+= roboto_cond.getsize(i)[0]+40

        bg.save("rank.png")

    def user_entry(self, user: discord.Member):
        member_info = {}
        member_info["name"] = user.name
        member_info["xp"] = 0
        member_info["level"] = 1
        member_info["rank"] = 0
        member_info["role"] = "Prostitute"
        member_info["messages"] = 1
        member_info["rel_bar"] = 100
        member_info["rel_xp"] = 0

        self.exp_info[user.id] = member_info
        gen.db_update("exp", self.exp_info)

        return member_info

  


    def get_designation(self, level: int()):
        a = list(self.roles.values())
        for i in range(len(a)):
            if a[i][0] >= level:
                break

        rel_role = a[i - 1][0]

        for role,level in self.roles.items():
            if level[0] == rel_role:
                return role

    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        
        if not message.author.bot:
            if message.author.id not in self.exp_info.keys() and not message.author.bot:
                member_info = self.user_entry(message.author)
            
            else:
                member_info = self.exp_info[message.author.id]

            member_info["active"] = True
            member_info["messages"] += 1

            self.exp_info[message.author.id] = member_info
          
        gen.db_update("exp", self.exp_info)



    @commands.command()
    async def rank(self, ctx,member = ''):
        try:
            int(member)
            
        except:
            try:
            
                member1 = member
                member1 = member1[3:-1]
                
                member1 = int(member1)
                member1 = ctx.channel.guild.get_member(member1)
            except :
            

                member1 = ctx.channel.guild.get_member_named(member)
                if not member1:
                
                    member = ctx.author
                else:
                    
                    member = member1
            else:
                member = member1
        else:
            member1 = ctx.channel.guild.get_member(int(member))
            if not member1:
                member = ctx.author
            else:
                member = member1
              
        thrd = Thread(target = self.rank_creation,args=(ctx,member))
        thrd.start()
        thrd.join()
        await ctx.send(file = discord.File("rank.png"))


def setup(client):
    client.add_cog(exp(client))
