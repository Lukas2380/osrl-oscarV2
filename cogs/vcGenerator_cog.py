import discord
from discord.ext import commands
from discord import Embed, app_commands
import asyncio
from data.helper_functions import *

class VCGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.created_channels = []
        self.load_generators()

    def load_generators(self):
        with open('./data/vcGenerator/generators.txt', 'r+') as file:
            data = file.read()
            self.vc_generators = data.split('\n')
            self.vc_generators.pop(-1)

    async def save_generators(self):
        with open('./data/vcGenerator/generators.txt', 'w') as file:
            for generator in self.vc_generators:
                file.write(f"{generator}\n")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await log(f"Voice state update event triggered: {member} moved from {before.channel} to {after.channel}")
        for vc_generator in self.vc_generators:
            vc_channel, generative_name, user_limit = vc_generator.split(',')

            if after.channel and str(after.channel.id) == vc_channel:
                await log(f'Someone joined a channel generator')
                # Create a new voice channel
                guild = member.guild
                generative_name = generative_name.replace("*", member.display_name)
                new_channel = await guild.create_voice_channel(generative_name, category = after.channel.category, user_limit = user_limit)
                await log(f'Made a temporary channel')
                await member.move_to(new_channel)
                await log(f'Moved the user to the temporary channel')
                self.created_channels.append(new_channel.id)

        await asyncio.sleep(3)
        
        # Check and delete empty channels
        for channel_id in self.created_channels:
            channel = member.guild.get_channel(channel_id)
            if channel and len(channel.members) == 0 and channel != after.channel:
                await log(f'Found an empty channel ... deleting it')
                self.created_channels.remove(channel_id)
                await channel.delete()

    @app_commands.command(name="list_vc_generators", description="List VC generators")
    async def list_vc_generators(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # List all VC generators and their generative names
        vcList = ""
        
        for generator in self.vc_generators:
            vc_id, generativeName, userLimit = generator.split(',')
            vcList += f"<#{vc_id}>; Name: User\'s {generativeName}; User limit: {userLimit}\n"

        response = Embed(title='List of VC Generators:', description=vcList, color=blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="add_vc_generator", description="Add a VC generator")
    @app_commands.describe(vc_channel="The VC channel to add", generative_name="The generative name, Example: 'Coach *`s vc' (The * will automatically be replaced with the users name)")
    async def add_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel, generative_name: str, user_limit: int):
        await interaction.response.defer()
        alreadyAGenerator = False
        for generator in self.vc_generators:
            if str(vc_channel.id) in generator:
                alreadyAGenerator = True
                response = Embed(title='Cant add Generator', description=f'VC Generator already exists', color=red)

        if not alreadyAGenerator:
            self.vc_generators.append(str(f'{str(vc_channel.id)},{generative_name},{str(user_limit)}'))
            await self.save_generators()

            response = Embed(title='Generator added', description=f'VC Generator was added: <#{str(vc_channel.id)}>', color=blue)
        
        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove_vc_generator", description="Remove a VC generator")
    @app_commands.describe(vc_channel="The VC channel to remove")
    async def remove_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        await interaction.response.defer()
        
        response = Embed(title="Error", description=f'This VC channel is not a VC generator.', color=red)
        # Remove the VC generator from the dictionary
        for generator in self.vc_generators:
            if str(vc_channel.id) in generator:
                self.vc_generators.remove(generator)
                await self.save_generators()

                response = Embed(title='Generator removed', description=f'VC Generator was removed: <#{str(vc_channel.id)}>', color=blue)
                break

        await interaction.followup.send(embed=response)


async def setup(bot):
    await bot.add_cog(VCGeneratorCog(bot))
