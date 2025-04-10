import discord
from discord import app_commands, Embed
from discord.ext import commands, tasks
from mcstatus.server import JavaServer  # Import JavaServer for Minecraft Java Edition

class MinecraftCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = JavaServer("144.217.48.9", 25568)  # IP and PORT as arguments for Java Edition
        self.channel_id = 1359911089659183134  # Replace this with your VC's channel ID
        self.update_vc.start()  # Start the periodic task

    @tasks.loop(minutes=5)  # Update every 5 minutes
    async def update_vc(self):
        try:
            # Get the Minecraft server status
            status = self.server.status()

            # Get the number of online players
            players_online = status.players.online

            # Get the voice channel by its ID
            channel = self.bot.get_channel(self.channel_id)

            # Update the channel name with the number of players
            await channel.edit(name=f"Players Online: {players_online}")

        except Exception as e:
            print(f"Error updating VC name: {str(e)}")

    """ @app_commands.command(name="mcstatus", description="Get the current status of the Minecraft server.")
    async def mcstatus(self, interaction: discord.Interaction):
        # Get the Minecraft server status
        try:
            status = self.server.status()

            # Get the players and TPS information
            players_online = status.players.online
            players_max = status.players.max
            tps = status.latency  # Get the latency, which is the closest to TPS in mcstatus 11.x.x
            version = status.version.name

            # Create an Embed object for better message formatting
            embed = Embed(title="Minecraft Server Status", color=discord.Color.green())
            embed.add_field(name="Players", value=f"{players_online}/{players_max}", inline=False)
            embed.add_field(name="Latency (TPS Approx)", value=f"{tps:.2f}ms", inline=False)
            embed.add_field(name="Version", value=version, inline=False)

        except Exception as e:
            embed = Embed(title="Error", description=f"Error getting server status: {str(e)}", color=discord.Color.red())

        # Send the Embed as a response
        await interaction.response.send_message(embed=embed) """

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MinecraftCog(bot))
