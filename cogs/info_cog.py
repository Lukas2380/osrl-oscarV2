import json
import sys
import discord
from discord.ext import commands
from discord import app_commands, TextChannel
from discord.ui import View, Button
from data.helper_functions import *

class Info_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load channel IDs from the text file at the start of the cog
        self.load_channel_ids()

    # Initialize variables with default values or None
    servrulesChannel = None
    servfaqChannel = None
    servanonrepChannel = None 
    servdirChannel = None
    servstaffChannel = None
    ladderrulesChannel = None
    ladderadmininfoChannel = None
    ladderinfoChannel = None
    mcinfoChannel = None

    def load_channel_ids(self):
        file_path = './data/info/setchannels.txt'

        with open(file_path, 'r') as file:
            for line in file:
                # Split the line into name and ID
                name, channel_id = line.strip().split('=')

                # Update the corresponding variable
                setattr(self, name, int(channel_id))

    def save_channel_ids(self):
        channels_data = {
            "servrulesChannel": self.servrulesChannel,
            "servfaqChannel": self.servfaqChannel,
            "servanonrepChannel": self.servanonrepChannel,
            "servdirChannel": self.servdirChannel,
            "servstaffChannel": self.servstaffChannel,
            "ladderrulesChannel": self.ladderrulesChannel,
            "ladderadmininfoChannel": self.ladderadmininfoChannel,
            "ladderinfoChannel": self.ladderinfoChannel,
            "mcinfoChannel": self.mcinfoChannel,
        }

        with open('./data/info/setchannels.txt', 'w') as file:
            for channel_name, channel_id in channels_data.items():
                file.write(f"{channel_name}={channel_id}\n")

    @app_commands.command(name="info-setchannels", description="Set channels for the info embeds")
    async def set_channels(self, interaction, servrules: TextChannel, servfaq: TextChannel, servanonrep: TextChannel, servdir: TextChannel, servstaff: TextChannel, ladderrules: TextChannel, ladderadmininfo: TextChannel, ladderinfo: TextChannel, mcinfo: TextChannel):
        await interaction.response.defer()
        self.servrulesChannel = servrules.id
        self.servfaqChannel = servfaq.id
        self.servanonrepChannel = servanonrep.id
        self.servdirChannel = servdir.id
        self.servstaffChannel = servstaff.id
        self.ladderrulesChannel = ladderrules.id
        self.ladderadmininfoChannel = ladderadmininfo.id
        self.ladderinfoChannel = ladderinfo.id
        self.mcinfoChannel = mcinfo.id

        # Save channel IDs to the text file
        self.save_channel_ids()
        await interaction.followup.send("Channels have been set.")

    @app_commands.command(name="info-resend", description="Resend one of the info texts")
    async def info_send(self, interaction, info: typing.Literal["servrules", "servfaq", "servanonrep", "servdir", "servstaff", "ladderrules", "ladderadmininfo", "ladderinfo", "mcinfo"]):
        await interaction.response.defer()
        channel = None
        title = ""

        match info:
            case "servrules":
                channel = self.bot.get_channel(self.servrulesChannel)
                title='Old School Server Rules'
            case "servfaq":
                channel = self.bot.get_channel(self.servfaqChannel)
                title='Frequently Asked Questions'
            case "servanonrep":
                channel = self.bot.get_channel(self.servanonrepChannel)
                title='Anonymous Reporting Form'
            case "servdir":
                channel = self.bot.get_channel(self.servdirChannel)
                title='Old School Server Directory'
            case "servstaff":
                channel = self.bot.get_channel(self.servstaffChannel)
                title='Server Staff List'
            case "ladderrules":
                channel = self.bot.get_channel(self.ladderrulesChannel)
                title='1v1 Ladder Rules'
            case "ladderadmininfo":
                channel = self.bot.get_channel(self.ladderadmininfoChannel)
                title='1v1 Ladder Admin Commands'
            case "ladderinfo":
                channel = self.bot.get_channel(self.ladderinfoChannel)
                title='1v1 Ladder Commands and Info'
            case "mcinfo":
                channel = self.bot.get_channel(self.mcinfoChannel)
                title='Minecraft Server Info'

        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        await channel.purge(limit=1)

        with open("data/info/" + info + ".txt", 'r') as file:
            body = file.read()

        embed = discord.Embed(
            title=title,
            description=body,
            color=infoEmbedColor
        )
        embed.set_footer(text="Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")

        await channel.send(embed=embed)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))