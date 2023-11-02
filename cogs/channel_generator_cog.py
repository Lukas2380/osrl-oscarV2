import discord
from discord.ext import commands
import asyncio

class ChannelGeneratorCog(commands.Cog):
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

async def setup(bot):
    await bot.add_cog(ChannelGeneratorCog(bot))
