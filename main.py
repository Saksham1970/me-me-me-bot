import discord
from discord.ext import commands, tasks
from itertools import cycle
import os
import sys
import general as gen
import json
import asyncio
from colorama import init, Fore, Back, Style
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
async def backup(ctx, msg=""):
    gen.commit("Manual command commit, " + msg)
    if not msg == "":
        await ctx.send(">>> Everything backed up with message - ```" + msg + "```, boss")
    else:
        await ctx.send(">>> Everything backed up with no message because your lazy ass could'nt be bothered to type")


# ? EVENTS

# * STATUS CHANGE
@tasks.loop(seconds=6)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

# * ON READY
@client.event
async def on_ready():
    change_status.start()
    cog_load_startup()
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
    gen.error_message(error)


TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)
