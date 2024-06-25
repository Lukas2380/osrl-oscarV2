import discord
from discord.ext import commands
from discord import Embed, app_commands
import asyncio
from data.helper_functions import *

class VCGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel:
            channel_id = str(after.channel.id)

            # Query the database for the given channel ID
            response = vcGeneratorsTable.select("*").eq("vc_id", channel_id).execute()

            # Check if the response contains data
            if response and len(response.data) > 0:
                # Assume response.data[0] contains the relevant data from the database
                record = response.data[0]

                # Extract necessary information from the database record
                generative_name = record.get('vc_name', 'Temporary Channel')
                user_limit = record.get('vc_userlimit', 0)  # Default user limit if not provided

                await log(f'Someone joined a channel generator')
                
                # Create a new temporary voice channel
                guild = member.guild
                generative_name = generative_name.replace("*", member.display_name)
                new_channel = await guild.create_voice_channel(
                    generative_name,
                    category=after.channel.category,
                    user_limit=user_limit
                )
                
                await log(f'Made a temporary channel')
                await member.move_to(new_channel)
                await log(f'Moved the user to the temporary channel')
                
                # Insert the new channel's ID into the temporaryVC table
                temporaryVCTable.insert({"vc_id": new_channel.id}).execute()
                await log(f'Inserted the new channel ID into the database')

        await asyncio.sleep(3)
        
        # Check and delete empty channels
        response = temporaryVCTable.select("vc_id").execute()

        if response and len(response.data) > 0:
            for record in response.data:
                temp_channel_id = record["vc_id"]
                temp_channel = member.guild.get_channel(temp_channel_id)
                if temp_channel and len(temp_channel.members) == 0 and temp_channel != after.channel:
                    await log(f'Found an empty temporary channel ... deleting it')
                    try:
                        # Remove the channel from the database
                        temporaryVCTable.delete().eq("vc_id", temp_channel_id).execute()
                        await temp_channel.delete()
                    except Exception as e:
                        await log(f"Error while trying to delete channel: {temp_channel_id} - {str(e)}")
                elif not temp_channel:
                    temporaryVCTable.delete().eq("vc_id", temp_channel_id).execute()
                    await log(f'Found an already deleted temporary channel ... deleting it from the db')

    @app_commands.command(name="vcgen-list", description="List VC generators")
    async def list_vc_generators(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Query the database to get all VC generators
        response = temporaryVCTable.select("*").execute()
        
        if response and len(response.data) > 0:
            vcList = ""
            for generator in response.data:
                vc_id = generator["vc_id"]
                generativeName = generator["vc_name"]
                userLimit = generator["vc_userlimit"]
                vcList += f"<#{vc_id}>; Name: {generativeName}; User limit: {userLimit}\n"
            
            response_embed = Embed(title='List of VC Generators:', description=vcList, color=discord.Color.blue())
        else:
            response_embed = Embed(title='List of VC Generators:', description='No VC generators found.', color=discord.Color.blue())
        
        await interaction.followup.send(embed=response_embed)


    @app_commands.command(name="vcgen-add", description="Add a VC generator")
    @app_commands.describe(vc_channel="The VC channel to add", generative_name="The generative name, Example: 'Coach *`s vc' (The * will automatically be replaced with the users name)", user_limit="0 is no limit")
    async def add_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel, generative_name: str, user_limit: int):
        await interaction.response.defer()

        # Query the database to check if the generator already exists
        response = vcGeneratorsTable.select("*").eq("vc_id", str(vc_channel.id)).execute()
        
        if response and len(response.data) > 0:
            # If the generator already exists
            response_embed = Embed(
                title='Cannot add Generator',
                description='VC Generator already exists',
                color=discord.Color.red()
            )
        else:
            # Insert the new generator into the database
            vcGeneratorsTable.insert({
                "vc_id": str(vc_channel.id),
                "vc_name": generative_name,
                "vc_userlimit": user_limit
            }).execute()
            
            response_embed = Embed(
                title='Generator added',
                description=f'VC Generator was added: <#{str(vc_channel.id)}>',
                color=discord.Color.blue()
            )

        await interaction.followup.send(embed=response_embed)

    @app_commands.command(name="vcgen-remove", description="Remove a VC generator")
    @app_commands.describe(vc_channel="The VC channel to remove")
    async def remove_vc_generator(self, interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
        await interaction.response.defer()

        # Query the database to check if the generator exists
        response = vcGeneratorsTable.select("*").eq("vc_id", str(vc_channel.id)).execute()
        
        if response and len(response.data) > 0:
            # Remove the generator from the database
            vcGeneratorsTable.delete().eq("vc_id", str(vc_channel.id)).execute()
            
            response_embed = Embed(
                title='Generator removed',
                description=f'VC Generator was removed: <#{str(vc_channel.id)}>',
                color=discord.Color.blue()
            )
        else:
            response_embed = Embed(
                title="Error",
                description=f'This VC channel is not a VC generator.',
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=response_embed)


async def setup(bot):
    await bot.add_cog(VCGeneratorCog(bot))
