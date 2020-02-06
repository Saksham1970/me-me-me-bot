import discord
from discord.ext import commands, tasks


        
class MyHelpCommand(commands.HelpCommand):
    
    def __init__(self):
        super().__init__(command_attrs={
	    		'help': 'Shows help about the bot, a command, or a category',
	    		'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member)})
    nsfw_cog_name = "nsfw"
    def get_command_signature(self, command):
        """Method to return a commands name and signature"""
        if not command.signature and not command.parent:  # checking if it has no args and isn't a subcommand
            return f'`ME!` `{command.name}`'
        if command.signature and not command.parent:  # checking if it has args and isn't a subcommand
            return f'`ME!` `{command.name}` `{command.signature}`'
        if not command.signature and command.parent:  # checking if it has no args and is a subcommand
            return f'`ME!` `{command.parent.name}` `{command.name}`'
        else:  # else assume it has args a signature and is a subcommand
            return f'`ME!` `{command.parent.name}` `{command.name}` `{command.signature}`'

    def get_command_aliases(self, command):  # this is a custom written method along with all the others below this
        """Method to return a commands aliases"""
        if not command.aliases:  # check if it has any aliases
            return ''
        else:
            return f'`({"` | `".join([alias for alias in command.aliases])})`'

    def get_command_description(self, command):
        """Method to return a commands short doc/brief"""
        if not command.short_doc:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc

    def get_command_help(self, command):
        """Method to return a commands full description/doc string"""
        if not command.help:  # check if it has any brief or doc string
            return 'There is no documentation for this command currently'
        else:
            return command.help


    async def send_bot_help(self, mapping):
   
        ctx=self.context
        embeds=[]
        cogs_list = []

        for cog in mapping:
            if cog:
                cog_name = cog.qualified_name

                try:
                    emoji,desc = cog.description.split(maxsplit = 1)
                except:
                    emoji = ":construction_worker:"
                    desc = "This is under construction, Now Skiddadle Skidoodle."
                embeds += [discord.Embed(title = f"{emoji} **{cog_name}** ", description = desc)]
                

                for command in mapping[cog]:
                    
                    embeds[len(cogs_list)].add_field(name = f'{self.get_command_signature(command)} {self.get_command_aliases(command)}',value = self.get_command_description(command))

                 
                cogs_list+=[cog_name]
        embed = discord.Embed(title = "ME! HELP",description = "Yet to be filled")
                
        for cog in mapping:
            try:
                emoji,desc = cog.description.split(maxsplit=1)
            except:
                emoji = ":construction_worker:"
                desc = "This is under construction, Now Skiddadle Skidoodle."
            if cog:
                cog_name = cog.qualified_name
                embed.add_field(name = f"{emoji} **{cog_name}**", value= f">>> `ME! HELP {cog_name}`")
        embeds.insert(0,embed)
        
        wait_time = 180
        page = 0 
        embed_msg = await ctx.send(embed = embeds[0])
        embed_msg: discord.Message

        async def reactions_add(message, reactions):
                for reaction in reactions:
                    await message.add_reaction(reaction)
        reactions = {"back": "⬅", "forward": "➡", "nsfw": "🍆", "delete": "❌"}
        ctx.bot.loop.create_task(reactions_add(embed_msg, reactions.values())) 

        def check(reaction: discord.Reaction, user):  
                return user == ctx.author and reaction.message.id == embed_msg.id

        while True:

            try:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=wait_time, check=check)
            
            except TimeoutError:
                await ctx.send(f">>> Deleted Help Command due to inactivity.")
                await embed_msg.delete()

                return

            else: 
                await embed_msg.remove_reaction(str(reaction.emoji), ctx.author)

                if str(reaction.emoji) in reactions.values():

                    if str(reaction.emoji) == reactions["forward"]: 
                        page += 1
                        
                        if page >= len(embeds):
                            page = len(embed)-1

                        
                        await embed_msg.edit(embed=embeds[page])

                    elif str(reaction.emoji) == reactions["back"]: 
                        page -= 1

                        if page < 0:
                            page = 0
                        
                        
                        await embed_msg.edit(embed=embeds[page])

                    elif str(reaction.emoji) == reactions["nsfw"]: 
                        page = cogs_list.index(self.nsfw_cog_name)
                     
                        await embed_msg.edit(embed=embeds[page+1])


                    elif str(reaction.emoji) == reactions["delete"]: 
                        await embed_msg.delete(delay=1)
                        return
                else:
                    pass
    
    async def send_command_help(self, command):
        ctx=self.context
      
        embed = discord.Embed(title =  f"{self.get_command_signature(command)} {self.get_command_aliases(command)}",description=self.get_command_help(command))
        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        ctx=self.context
        try:
            emoji,desc = cog.description.split(maxsplit = 1)
        except:
            emoji = ":construction_worker:"
            desc = "This is under construction, Now Skiddadle Skidoodle."
        embed = discord.Embed(title = f"{cog.qualified_name} {emoji}", description = desc)
        for command in cog.get_commands():
            embed.add_field(name = f'{self.get_command_signature(command)} {self.get_command_aliases(command)}',value = self.get_command_description(command))
        await ctx.send(embed=embed)
    
    async def send_group_help(self, group):
        ctx=self.context

        parent_command = list(group.commands)[0].parent
        embed = discord.Embed(title =  f"{self.get_command_signature(parent_command)} {self.get_command_aliases(parent_command)}",description=self.get_command_help(parent_command))
        for command in group.commands:
            embed.add_field(name = f'{self.get_command_signature(command)} {self.get_command_aliases(command)}',value = self.get_command_description(command))
        await ctx.send(embed=embed)
    