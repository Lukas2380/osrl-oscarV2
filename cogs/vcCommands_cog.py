import discord
from discord.ext import commands
from discord import app_commands

class VCCommands_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list_vc_generators", description="List VC generators")
    async def list_vc_generators(self, interaction: discord.Interaction):
        # List all VC generators and their generative names
        response = "List of VC Generators:\n"
        print(self.bot.vc_generators.items())
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


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(VCCommands_Cog(bot))