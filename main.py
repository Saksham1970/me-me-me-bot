from dotenv import load_dotenv
load_dotenv()

import os

import discord
from discord.ext import commands, tasks

from itertools import cycle
import general as gen
import asyncio



#! ME inside

# * CLIENT FUNCTIONS
prefix = gen.permu("me! ") + gen.permu("epic ")
client = commands.Bot(command_prefix=prefix, case_insensitive=True)
client.remove_command("help")
status = cycle(gen.status)

# * COG SET UP STUFF
@client.command(aliases=["enable"])
async def load(ctx, extension):
    found = False
    for role in ctx.author.roles:
        if role.id == gen.admin_role_id:
            found = True
            client.load_extension(f"cogs.{extension}")
            await ctx.send(f">>> {extension.capitalize()} commands are now ready to deploy.")
    if not found:
        await ctx.send(f">>> You thought that you could do that? How Cute.")


@client.command(aliases=["disable"])
async def unload(ctx, extension):
    found = False
    for role in ctx.author.roles:
        if role.id == gen.admin_role_id:
            found = True
            client.unload_extension(f"cogs.{extension}")
            await ctx.send(f">>> {extension.capitalize()} commands were stopped, Master. ")
    if not found:
        await ctx.send(f">>> You thought that you could do that? How Cute.")


@client.command(aliases=["refresh"])
async def reload(ctx, extension):
    found = False
    for role in ctx.author.roles:
        if role.id == gen.admin_role_id:
            found = True
            client.unload_extension(f"cogs.{extension}")
            client.load_extension(f"cogs.{extension}")
            await ctx.send(f">>> {extension.capitalize()} commands drank some coke, they are now refreshed. ")
    if not found:
        await ctx.send(f">>> You thought that you could do that? How Cute.")


def cog_load_startup():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

# * BACKING UP AND COMMIT STUFF
@client.command(aliases=["commit", "baccup"])
async def backup(ctx, *, msg=""):

    found = False
    for role in ctx.author.roles:
        if role.id == gen.admin_role_id:
            found = True
    if found:
        done = gen.commit("| Manual |" + msg)
        if not msg == "" and done:
            await ctx.send(f">>> Everything backed up with message - ```{msg}```")
        elif msg == "":
            await ctx.send(">>> Everything backed up with no message because your lazy ass could'nt be bothered to type")
        else:
            await ctx.send(">>> Couldn't Backup Since Commit upto the mark.")
    else:
        await ctx.send("Shut Up")

@client.command(aliases=["Debug","Development"])
async def develop(ctx , on_off):
    
    found = False
    for role in ctx.author.roles:                                                                               #! TODO make this a function
            if role.id == gen.admin_role_id:
                found=True    
    if not found:
        await ctx.send("SHUT UP.")
        return
    var = gen.db_receive("var")
    if on_off.lower() == "on" or on_off.lower() == "true":    
        var["DEV"] = 1
        await ctx.send("DONE.") 
    elif on_off.lower() == "off" or on_off.lower() == "false":    
        var["DEV"] = 0
        await ctx.send("DONE.")
    else:
        await ctx.send("ITS on OR off. (True or False).")
    gen.db_update("var",var)

# ? EVENTS

# * STATUS CHANGE
@tasks.loop(seconds=6)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@tasks.loop(hours = 24)
async def auto_backup():
    if not gen.db_receive("var")["DEV"]:
        gen.commit("| Auto |")

# * ON READY
@client.event
async def on_ready():
    change_status.start()
    cog_load_startup()
    
    auto_backup.start() 
    gen.reset()

    print('Bot is ready as sef!')

# * DELAYS FOR INTAKE
@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    await client.invoke(ctx)

# * COMMAND NOT FOUND
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(">>> That isn't even a command, you have again proven to be a ME!stake.")
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=1)
    if not isinstance(error,commands.MissingRequiredArgument):
        gen.error_message(error)


TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)
