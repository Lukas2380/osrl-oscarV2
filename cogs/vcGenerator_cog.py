import discord
from discord.ext import commands
from discord import Embed, app_commands
import asyncio

class VCGeneratorCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.created_channels = []
        self.bot.vc_generators = []
        #self.load_generators()

    red = 0xFF5733
    blue = 0x0CCFFF

    def load_generators(self):
        try:
            with open('./data/vcGenerator/generators.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    data = line.split(',')
                    vc_channel_id = int(data[0])
                    generative_name = data[1]
                    user_limit = int(data[2])
                    # Create a dictionary for the generator
                    generator = {
                        'vc_channel': vc_channel_id,
                        'generative_name': generative_name,
                        'user_limit': user_limit
                    }
                    self.bot.vc_generators.append(generator)

            print(type(self.bot.vc_generators))
        except Exception as e:
            print(e)

    async def save_generators(self):
        with open('./data/vcGenerator/generators.txt', 'w') as file:
            for generator in self.bot.vc_generators:
                vc_channel_id = generator['vc_channel']
                generative_name = generator['generative_name']
                user_limit = generator['user_limit']
                file.write(f"{vc_channel_id},{generative_name},{user_limit}\n")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"Voice state update event triggered: {member} moved from {before.channel} to {after.channel}")
        for vc_generator in self.bot.vc_generators:
            vc_channel = vc_generator['vc_channel']
            generative_name = vc_generator['generative_name']
            user_limit = vc_generator['user_limit']
            if after.channel and after.channel.id == vc_channel:
                print(f'Someone joined a channel generator')
                # Create a new voice channel
                guild = member.guild
                new_channel = await guild.create_voice_channel(f'{member.display_name}{generative_name}', category = after.channel.category, user_limit = user_limit)
                print(f'Made a temporary channel')
                await member.move_to(new_channel)
                print(f'Moved the user to the temporary channel')
                self.created_channels.append(new_channel.id)

        await asyncio.sleep(3)
        
        # Check and delete empty channels
        for channel_id in self.created_channels:
            channel = member.guild.get_channel(channel_id)
            if channel and len(channel.members) == 0 and channel != after.channel:
                print(f'Found an empty channel ... deleting it')
                self.created_channels.remove(channel_id)
                await channel.delete()

    @app_commands.command(name="list_vc_generators", description="List VC generators")
    async def list_vc_generators(self, interaction: discord.Interaction):
        # List all VC generators and their generative names
        vcList = "List of VC Generators:\n"   
        
        for generator in self.bot.vc_generators:
            vcList += f"{generator['vc_channel']}; Name: {generator['generative_name']}; User limit: {generator['user_limit']}\n"

        response = Embed(title='Generator added', description=vcList, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="add_vc_generator", description="Add a VC generator")
    @app_commands.describe(vc_channel="The VC channel to add", generative_name="The generative name")
    async def add_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel, generative_name: str, user_limit: int):
        try:
            new_vc_generator = {
                'vc_channel': vc_channel.id,
                'generative_name': generative_name,
                'user_limit': user_limit
            }
            print(type(self.bot.vc_generators))
            self.bot.vc_generators.append(new_vc_generator)
            await self.save_generators()

            response = Embed(title='Generator added', description=f'VC Generator was added: {generative_name}', color=self.blue)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            print(e)

    @app_commands.command(name="remove_vc_generator", description="Remove a VC generator")
    @app_commands.describe(vc_channel="The VC channel to remove")
    async def remove_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        try:
            response = Embed(title="Error", description=f'This VC channel is not a VC generator.', color=self.red)
            # Remove the VC generator from the dictionary
            for generator in self.bot.vc_generators:
                if generator['vc_channel'] == vc_channel.id:
                    self.bot.vc_generators.remove(generator)
                    await self.save_generators()

                    response = Embed(title='Generator removed', description=f'VC Generator was removed: {generator}', color=self.blue)
                    break

            await interaction.response.send_message(embed=response)

        except Exception as e:
            print(f'Error removing VC generator: {str(e)}')

async def setup(bot):
    await bot.add_cog(VCGeneratorCog(bot))
