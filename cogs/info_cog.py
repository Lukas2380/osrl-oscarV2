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
    rulesChannel = None
    faqChannel = None
    anonrepChannel = None 
    servdirChannel = None
    servstaffChannel = None
    ladderrulesChannel = None
    ladderadmininfoChannel = None
    ladderinfoChannel = None

    footerText = "Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you"

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
            "servrules": self.rulesChannel,
            "faq": self.faqChannel,
            "anonrep": self.anonrepChannel,
            "servdir": self.servdirChannel,
            "servstaff": self.servstaffChannel,
            "1v1rules": self.ladderrulesChannel,
            "admininfo": self.ladderadmininfoChannel,
            "1v1info": self.ladderinfoChannel
        }

        with open('./data/info/setchannels.txt', 'w') as file:
            for channel_name, channel_id in channels_data.items():
                file.write(f"{channel_name}={channel_id}\n")

    @app_commands.command(name="info-setchannels", description="Set channels for the info embeds")
    async def set_channels(self, interaction, rules: TextChannel, faq: TextChannel, anonrep: TextChannel, servdir: TextChannel, servstaff: TextChannel, ladderrules: TextChannel, ladderadmininfo: TextChannel, ladderinfo: TextChannel):
        await interaction.response.defer()
        self.rulesChannel = rules.id
        self.faqChannel = faq.id
        self.anonrepChannel = anonrep.id
        self.servdirChannel = servdir.id
        self.servstaffChannel = servstaff.id
        self.ladderrulesChannel = ladderrules.id
        self.ladderadmininfoChannel = ladderadmininfo.id
        self.ladderinfoChannel = ladderinfo.id

        # Save channel IDs to the text file
        self.save_channel_ids()

        await interaction.followup.send("Channels have been set.")

    @app_commands.command(name="info-servrules", description="Resend the rules embed")
    async def servrules(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.rulesChannel)

        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))

        await channel.purge(limit=1)

        with open('./data/info/servrules.txt', 'r') as file:
            serv = file.read()
        serv = discord.Embed(
            title='Old School Server Rules',
            description=serv,
            color=infoEmbedColor
        )
        serv.set_footer(text=self.footerText)
        await channel.send(embed=serv)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-servfaq", description="Resend the faq embed")
    async def servfaq(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.faqChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)

        with open('./data/info/faq.txt', 'r') as file:
            faq = file.read()
        faq = discord.Embed(
            title='Frequently Asked Questions',
            description=faq,
            color=infoEmbedColor
        )
        faq.set_footer(text=self.footerText)
        await channel.send(embed=faq)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)

    @app_commands.command(name="info-servanonrep", description="Resend the anonrep embed")
    async def servanonrep(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.anonrepChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/anonrep.txt', 'r') as file:
            anonrep = file.read()
        report = discord.Embed(
            title='Anonymous Reporting Form',
            description=anonrep,
            color=infoEmbedColor
        )
        report.set_footer(text=self.footerText)
        await channel.send(embed=report)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-servdir", description="Resend the servdir embed")
    async def servdir(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.servdirChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/servdir.txt', 'r') as file:
            servdir = file.read()
        
        servdirec = discord.Embed(title='Old School Server Directory', description=servdir, color=infoEmbedColor)
        servdirec.set_footer(text=self.footerText)
        await channel.send(embed=servdirec)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-servstaff", description="Resend the server staff embed")
    async def servstaff(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.servstaffChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/servstaff.txt', 'r') as file:
            servstaff = file.read()
        servstaffembed = discord.Embed(
            title='Server Staff List',
            description=servstaff,
            color=infoEmbedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-ladderrules", description="Resend the ladder rules embed")
    async def ladderrules(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.ladderrulesChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/1v1rules.txt', 'r') as file:
            rules = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Rules',
            description=rules,
            color=infoEmbedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-ladderadmininfo", description="Resend the ladder admin info embed")
    async def ladderadmininfo(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.ladderadmininfoChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/admininfo.txt', 'r') as file:
            admininfo = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder admin commands',
            description=admininfo,
            color=infoEmbedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        
    @app_commands.command(name="info-ladderinfo", description="Resend the ladder info embed")
    async def ladderinfo(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.ladderinfoChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        await channel.purge(limit=1)
        
        with open('./data/info/1v1info.txt', 'r') as file:
            info = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Commands and Info',
            description=info,
            color=infoEmbedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))