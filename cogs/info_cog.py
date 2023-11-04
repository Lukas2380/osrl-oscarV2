import discord
from discord.ext import commands
from discord import app_commands

class Info_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    footerText = "Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you"

    @app_commands.command(name="servrules", description="Resend the rules embed")
    async def servrules(self, interaction):
        channel = self.bot.get_channel(979020401621467178)
        with open('./data/servrules.txt', 'r') as file:
            serv = file.read()
        serv = discord.Embed(
            title='Old School Server Rules',
            description=serv,
            color=0x2ddaed
        )
        serv.set_footer(text=self.footerText)
        await channel.send(embed=serv)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="servfaq", description="Resend the faq embed")
    async def servfaq(self, interaction):
        channel = self.bot.get_channel(1089183143711494254)
        with open('./data/faq.txt', 'r') as file:
            faq = file.read()
        faq = discord.Embed(
            title='Frequently Asked Questions',
            description=faq,
            color=0x2ddaed
        )
        faq.set_footer(text=self.footerText)
        await channel.send(embed=faq)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="servanonrep", description="Resend the anonrep embed")
    async def servanonrep(self, interaction):
        channel = self.bot.get_channel(1099810839508303922)
        with open('./data/anonrep.txt', 'r') as file:
            anonrep = file.read()
        report = discord.Embed(
            title='Anonymous Reporting Form',
            description=anonrep,
            color=0x2ddaed
        )
        report.set_footer(text=self.footerText)
        await channel.send(embed=report)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="servdir", description="Resend the servdir embed")
    async def servdir(self, interaction):
        channel = self.bot.get_channel(1072889959226277978)
        with open('./data/welcome.txt', 'r') as file:
            welcome = file.read()
        with open('./data/rlconnect.txt', 'r') as file:
            rlconnect = file.read()
        with open('./data/tmsearch.txt', 'r') as file:
            tmsearch = file.read()
        with open('./data/coaching.txt', 'r') as file:
            coaching = file.read()
        servdirec = discord.Embed(title='Old School Server Directory', color=0x2ddaed)
        servdirec.add_field(name='Welcome', value=welcome, inline=False)
        servdirec.add_field(name='RL Connect', value=rlconnect, inline=False)
        servdirec.add_field(name='Teammate Search', value=tmsearch, inline=False)
        servdirec.add_field(name='Coaches Corner', value=coaching, inline=False)
        servdirec.set_footer(text=self.footerText)
        await channel.send(embed=servdirec)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="servstaff", description="Resend the server staff embed")
    async def servstaff(self, interaction):
        channel = self.bot.get_channel(1071431628666191962)
        with open('./data/servstaff.txt', 'r') as file:
            servstaff = file.read()
        servstaffembed = discord.Embed(
            title='Server Staff List',
            description=servstaff,
            color=0x2ddaed
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderrules", description="Resend the ladder rules embed")
    async def ladderrules(self, interaction):
        channel = self.bot.get_channel(1063875272950165504)
        with open('./data/1v1rules.txt', 'r') as file:
            rules = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Rules',
            description=rules,
            color=0x2ddaed
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderadmininfo", description="Resend the ladder admin info embed")
    async def ladderadmininfo(self, interaction):
        channel = self.bot.get_channel(1099011452389568673)
        with open('./data/admininfo.txt', 'r') as file:
            admininfo = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder admin commands',
            description=admininfo,
            color=0x2ddaed
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderinfo", description="Resend the ladder info embed")
    async def ladderinfo(self, interaction):
        channel = self.bot.get_channel(1099009440532938903)
        with open('./data/1v1info.txt', 'r') as file:
            info = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Commands and Info',
            description=info,
            color=0x2ddaed
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))