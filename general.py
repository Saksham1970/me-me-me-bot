import praw
import os
import discord
from colorama import init, Fore, Back ,Style
import json

roles = ['Prostitute','Rookie','Adventurer','Player','Hero']

status = ["Saksham's Son", 'Is Mayank','Who Is Gay']

subreddits = ["memes","dankmemes","cursedcomments","animemes"]

epic = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

admin_role_id = 632906375839744001 
MEE6_disc = 4876


level_Rookie=5
level_Adventurer=10
level_Player=25
level_Hero=50
level_CON=85

reddit = praw.Reddit(
client_id = os.environ.get("REDDIT_CLIENT_ID"),
client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
username= os.environ.get("REDDIT_USERNAME"),
password= os.environ.get("REDDIT_PASSWORD"),
user_agent="FuqU"
)



def permu(strs):
    if len(strs)==1:
        if strs.isalnum():
            return [strs.lower(),strs.upper()]
        else:
            return[strs]
    else:
        output = []
        f = strs[0]
        l=strs[1:]
        for st in permu(l):
            if f.isalnum():
                output.append(f.lower() + st)
                output.append(f.upper() + st)
            else:
                output.append(f+st)
        return output

def error_message(error):
    init(convert=True)
    print(Fore.BLACK + Back.WHITE + str(error))
    print(Fore.WHITE+Back.BLACK)
  
def db_receive(name):
    with open(f'{name}.json','r') as f:   
        return json.load(f)                                                                                       

def db_update(name,db):
    with open(f'{name}.json','w') as f:                                                                                            
        json.dump(db,f)

def new_entry(name,disc):
    mem_info=db_receive("inf")
    mem_info[disc] = {"name": name,"messages" : 0 , "level" : "Prostitute" , "coins" : 500}
    db_update("inf",mem_info)