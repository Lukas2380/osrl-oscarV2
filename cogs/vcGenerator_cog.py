import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class VCGeneratorCog(commands.Cog):
    created_channels = []  # Initialize a global list to track created channels

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"Voice state update event triggered: {member} moved from {before.channel} to {after.channel}")
        for vc, generative_name in self.bot.vc_generators.items():
            if after.channel and after.channel.id == vc.id:
                print(f'Someone joined a channel generator')
                # Create a new voice channel
                guild = member.guild
                new_channel = await guild.create_voice_channel(f'{member.display_name}{generative_name}', category = after.channel.category)
                print(f'Made a temporary channel')
                await member.move_to(new_channel)
                print(f'Moved the user to the temporary channel')
                self.created_channels.append(new_channel.id)
                # print(self.created_channels)

        # Delay the check and delete process by a few seconds (adjust the time as needed)
        await asyncio.sleep(5)
        
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
        response = "List of VC Generators:\n"   
        
        for vc, generative_name in self.bot.vc_generators.items():
            if vc:
                response += f"{vc.name}: User{generative_name}\n"
        await interaction.response.send_message(content=response)

    @app_commands.command(name="add_vc_generator", description="Add a VC generator")
    @app_commands.describe(vc_channel="The VC channel to add", generative_name="The generative name")
    async def add_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel, generative_name: str):
        # Store the VC channel and its generative name in the dictionary
        self.bot.vc_generators[vc_channel] = generative_name
        await interaction.response.send_message(f"VC Generator added: {generative_name}")

    @app_commands.command(name="remove_vc_generator", description="Remove a VC generator")
    @app_commands.describe(vc_channel="The VC channel to remove")
    async def remove_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        # Remove the VC generator from the dictionary
        if vc_channel in self.bot.vc_generators:
            generative_name = self.bot.vc_generators.pop(vc_channel)
            await interaction.response.send_message(f"VC Generator removed: {generative_name}")
        else:
            await interaction.response.send_message("This VC channel is not a VC generator.")

async def setup(bot):
    await bot.add_cog(VCGeneratorCog(bot))
