import discord
from discord.ext import commands
from discord import Embed, app_commands
import asyncio

class VCGeneratorCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.created_channels = []
        self.load_generators()

    red = 0xFF5733
    blue = 0x0CCFFF

    osrl_Server = 979020400765841462 # This is the OSRL Server ID
    log_channel = 1199387324904112178 # This is the id of the log channel in the OSRL Server

    async def log(self, output: str):
        guild = self.bot.get_guild(self.osrl_Server)
        channel = guild.get_channel(self.log_channel)
        await channel.send("```" + output + "```")

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
        await self.log(f"Voice state update event triggered: {member} moved from {before.channel} to {after.channel}")
        for vc_generator in self.vc_generators:
            vc_channel, generative_name, user_limit = vc_generator.split(',')

            if after.channel and str(after.channel.id) == vc_channel:
                await self.log(f'Someone joined a channel generator')
                # Create a new voice channel
                guild = member.guild
                new_channel = await guild.create_voice_channel(f'{member.display_name}\'s {generative_name}', category = after.channel.category, user_limit = user_limit)
                await self.log(f'Made a temporary channel')
                await member.move_to(new_channel)
                await self.log(f'Moved the user to the temporary channel')
                self.created_channels.append(new_channel.id)

        await asyncio.sleep(3)
        
        # Check and delete empty channels
        for channel_id in self.created_channels:
            channel = member.guild.get_channel(channel_id)
            if channel and len(channel.members) == 0 and channel != after.channel:
                await self.log(f'Found an empty channel ... deleting it')
                self.created_channels.remove(channel_id)
                await channel.delete()

    @app_commands.command(name="list_vc_generators", description="List VC generators")
    async def list_vc_generators(self, interaction: discord.Interaction):
        # List all VC generators and their generative names
        vcList = ""
        
        for generator in self.vc_generators:
            vc_id, generativeName, userLimit = generator.split(',')
            vcList += f"<#{vc_id}>; Name: User\'s {generativeName}; User limit: {userLimit}\n"

        response = Embed(title='List of VC Generators:', description=vcList, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="add_vc_generator", description="Add a VC generator")
    @app_commands.describe(vc_channel="The VC channel to add", generative_name="The generative name")
    async def add_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel, generative_name: str, user_limit: int):
        alreadyAGenerator = False
        for generator in self.vc_generators:
            if str(vc_channel.id) in generator:
                alreadyAGenerator = True
                response = Embed(title='Cant add Generator', description=f'VC Generator already exists', color=self.red)

        if not alreadyAGenerator:
            self.vc_generators.append(str(f'{str(vc_channel.id)},{generative_name},{str(user_limit)}'))
            await self.save_generators()

            response = Embed(title='Generator added', description=f'VC Generator was added: {generative_name}', color=self.blue)
        
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="remove_vc_generator", description="Remove a VC generator")
    @app_commands.describe(vc_channel="The VC channel to remove")
    async def remove_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        
        response = Embed(title="Error", description=f'This VC channel is not a VC generator.', color=self.red)
        # Remove the VC generator from the dictionary
        for generator in self.vc_generators:
            if str(vc_channel.id) in generator:
                self.vc_generators.remove(generator)
                await self.save_generators()

                response = Embed(title='Generator removed', description=f'VC Generator was removed: <#{str(vc_channel.id)}>', color=self.blue)
                break

        await interaction.response.send_message(embed=response)


async def setup(bot):
    await bot.add_cog(VCGeneratorCog(bot))
