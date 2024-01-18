import discord
from discord.ext import commands
from discord import app_commands, TextChannel
from discord.ui import View, Button

class Info_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    embedColor = 0x03fc0b

    footerText = "Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you"

    rulesChannel = None
    faqChannel = None
    anonrepChannel = None
    servdirChannel = None
    servstaffChannel = None
    ladderrulesChannel = None
    ladderadmininfoChannel = None
    ladderinfoChannel = None
    rolesChannel = 1182412867962687600

    @app_commands.command(name="setchannels", description="Set channels for the info embeds")
    async def set_channels(self, interaction, rules: TextChannel, faq: TextChannel, anonrep: TextChannel, servdir: TextChannel, servstaff: TextChannel, ladderrules: TextChannel, ladderadmininfo: TextChannel, ladderinfo: TextChannel, roles: TextChannel):
        self.rulesChannel = rules.id
        self.faqChannel = faq.id
        self.anonrepChannel = anonrep.id
        self.servdirChannel = servdir.id
        self.servstaffChannel = servstaff.id
        self.ladderrulesChannel = ladderrules.id
        self.ladderadmininfoChannel = ladderadmininfo.id
        self.ladderinfoChannel = ladderinfo.id
        self.rolesChannel = roles.id

        await interaction.response.send_message("Channels have been set.")

    @app_commands.command(name="servrules", description="Resend the rules embed")
    async def servrules(self, interaction):
        channel = self.bot.get_channel(self.rulesChannel)
        if channel:
            with open('./data/info/servrules.txt', 'r') as file:
                serv = file.read()
            serv = discord.Embed(
                title='Old School Server Rules',
                description=serv,
                color=self.embedColor
            )
            serv.set_footer(text=self.footerText)
            await channel.send(embed=serv)
            response = discord.Embed(title='Embed Sent')
        else:
            response = discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command.")
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="servfaq", description="Resend the faq embed")
    async def servfaq(self, interaction):
        channel = self.bot.get_channel(self.faqChannel)
        with open('./data/info/faq.txt', 'r') as file:
            faq = file.read()
        faq = discord.Embed(
            title='Frequently Asked Questions',
            description=faq,
            color=self.embedColor
        )
        faq.set_footer(text=self.footerText)
        await channel.send(embed=faq)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="servanonrep", description="Resend the anonrep embed")
    async def servanonrep(self, interaction):
        channel = self.bot.get_channel(self.anonrepChannel)
        with open('./data/info/anonrep.txt', 'r') as file:
            anonrep = file.read()
        report = discord.Embed(
            title='Anonymous Reporting Form',
            description=anonrep,
            color=self.embedColor
        )
        report.set_footer(text=self.footerText)
        await channel.send(embed=report)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="servdir", description="Resend the servdir embed")
    async def servdir(self, interaction):
        channel = self.bot.get_channel(self.servdirChannel)
        with open('./data/info/welcome.txt', 'r') as file:
            welcome = file.read()
        with open('./data/info/rlconnect.txt', 'r') as file:
            rlconnect = file.read()
        with open('./data/info/tmsearch.txt', 'r') as file:
            tmsearch = file.read()
        with open('./data/info/coaching.txt', 'r') as file:
            coaching = file.read()
        servdirec = discord.Embed(title='Old School Server Directory', color=self.embedColor)
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
        channel = self.bot.get_channel(self.servstaffChannel)
        with open('./data/info/servstaff.txt', 'r') as file:
            servstaff = file.read()
        servstaffembed = discord.Embed(
            title='Server Staff List',
            description=servstaff,
            color=self.embedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderrules", description="Resend the ladder rules embed")
    async def ladderrules(self, interaction):
        channel = self.bot.get_channel(self.ladderrulesChannel)
        with open('./data/info/1v1rules.txt', 'r') as file:
            rules = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Rules',
            description=rules,
            color=self.embedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderadmininfo", description="Resend the ladder admin info embed")
    async def ladderadmininfo(self, interaction):
        channel = self.bot.get_channel(self.ladderadmininfoChannel)
        with open('./data/info/admininfo.txt', 'r') as file:
            admininfo = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder admin commands',
            description=admininfo,
            color=self.embedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="ladderinfo", description="Resend the ladder info embed")
    async def ladderinfo(self, interaction):
        channel = self.bot.get_channel(self.ladderinfoChannel)
        with open('./data/info/1v1info.txt', 'r') as file:
            info = file.read()
        servstaffembed = discord.Embed(
            title='1v1 Ladder Commands and Info',
            description=info,
            color=self.embedColor
        )
        servstaffembed.set_footer(text=self.footerText)
        await channel.send(embed=servstaffembed)
        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)

    # ! update:
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Fetch the message object
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Check if the message was sent by the bot itself
        if message.author == self.bot.user:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            # Check if the member isn't the bot itself
            if member and not member.bot:
                # Here, you can add the logic to assign a role to the user
                role_name = str(payload.emoji).split(":")[1]
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    print(f"Assigned role '{role_name}' to {member.display_name}")
                else:
                    print(f"Role '{role_name}' not found.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author == self.bot.user:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if member and not member.bot:
                role_name = str(payload.emoji).split(":")[1]
                role = discord.utils.get(guild.roles, name=role_name)

                if role:
                    await member.remove_roles(role)
                    print(f"Removed role '{role_name}' from {member.display_name}")
                else:
                    print(f"Role '{role_name}' not found.")

    async def add_custom_reactions(self, sent_message, emoji_names, guild):
        for emoji_name in emoji_names:
            custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
            if custom_emoji:
                try:
                    await sent_message.add_reaction(custom_emoji)
                    print(f"Added reaction: {emoji_name}")
                except Exception as e:
                    print(e)
            else:
                print(f"Custom emoji '{emoji_name}' not found.")

    @app_commands.command(name="rolesembed", description="roles embed")
    async def rolesembed(self, interaction):
        channel = self.bot.get_channel(self.rolesChannel)
        role_names = []

        #region RolesIntroEmbed
        with open('./data/info/rolesintro.txt', 'r') as file:
            rolesintro = file.read()

        rolesIntroEmbed = discord.Embed(
            title='Assign your roles',
            description=rolesintro,
            color=self.embedColor
        )

        await channel.send(embed=rolesIntroEmbed)
        print("Rolesintro embed sent.")

        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)
        #endregion

        #region RankEmbed
        role_names = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Champ' ,'GC', 'SSL']
        
        # Create an embed
        rankEmbed = discord.Embed(
            title="Ranks",
            description="What is the highest rank you have achieved?",
            color=self.embedColor
        )
        sent_message = await channel.send(embed=rankEmbed)
        await self.add_custom_reactions(sent_message, role_names, interaction.guild)
        print("Rank embed sent.")
        #endregion

        #region RegionEmbed
        role_names = ['EU', 'SSL']

        regionEmbed = discord.Embed(
            title = 'Region',
            description= 'What region do you mostly play in?',
            color=self.embedColor
        )
        sent_message = await channel.send(embed=regionEmbed)
        await self.add_custom_reactions(sent_message, role_names, interaction.guild)
        print("Region embed sent.")
        #endregion

        #region System/ConsoleEmbed
        role_names = ['pc', 'xbox']

        platformEmbed = discord.Embed(
            title = 'System/Console',
            description= 'What system or console do you play on?',
            color=self.embedColor
        )

        sent_message = await channel.send(embed=platformEmbed)
        await self.add_custom_reactions(sent_message, role_names, interaction.guild)
        print("Platform embed sent")
        #endregion

        #region LfgEmbed
        role_names = ['LFG_RL', 'pc']

        lfgEmbed = discord.Embed(
            title = 'Looking for friends roles',
            description= 'These roles are for if you want to be notified when others are looking for people to play with.',
            color=self.embedColor
        )

        sent_message = await channel.send(embed=lfgEmbed)
        await self.add_custom_reactions(sent_message, role_names, interaction.guild)
        print("Lfg embed sent")
        #endregion

        #region Additional roles Embed
        role_names = ['pc']

        addRolesEmbed = discord.Embed(
            title = 'Additional Roles',
            description= 'These roles are specific interests that we offer in this discord! Choose any that you want to be a part of.',
            color=self.embedColor
        )

        sent_message = await channel.send(embed=addRolesEmbed)
        await self.add_custom_reactions(sent_message, role_names, interaction.guild)
        print("Additional Roles embed sent")
        #endregion




async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))