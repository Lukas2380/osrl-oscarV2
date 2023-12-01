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
    rolesChannel = None

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

    @app_commands.command(name="rolesembed", description="roles embed")
    async def rolesembed(self, interaction):
        channel = self.bot.get_channel(self.rolesChannel)

        async def button_callback(interaction, role_name):
            print(f"Processing button click for {role_name}.")

            # Get the user from the interaction
            user = interaction.user

            # Get the role to give (replace "RoleName" with the actual role name or ID)
            role = discord.utils.get(interaction.guild.roles, name=role_name)

            if role:
                print(f"Found role: {role.name} ({role.id})")

                # Check if the user already has the role
                if role in user.roles:
                    # User has the role, remove it
                    await user.remove_roles(role)
                    print(f"Role removed from {user.name} ({user.id})")

                    # Send an ephemeral message to the user in the server
                    content = f"You no longer have the role: {role_name}"
                    await interaction.response.send_message(content=content, ephemeral=True)
                else:
                    # User doesn't have the role, add it
                    await user.add_roles(role)
                    print(f"Role added to {user.name} ({user.id})")

                    # Send an ephemeral message to the user in the server
                    content = f"You now have the role: {role_name}"
                    await interaction.response.send_message(content=content, ephemeral=True)

                # Send a confirmation message in the text channel
                await interaction.response.send_message(f"Role operation completed for {user.mention}. Check your DMs for details.", ephemeral=True)
            else:
                print("Role not found.")
                await interaction.response.send_message("Role not found. Please contact an administrator.")

        #region RolesIntroEmbed

        with open('./data/info/rolesintro.txt', 'r') as file:
            rolesintro = file.read()

        rolesIntroEmbed = discord.Embed(
            title = 'Assign your roles',
            description=rolesintro,
            color=self.self.embedColor
        )

        await channel.send(embed=rolesIntroEmbed)
        print("Rolesintro embed sent.")

        response = discord.Embed(title='Embed Sent')
        await interaction.response.send_message(embed=response)

        #endregion

        #region RankEmbed

        # Create an embed
        rankEmbed = discord.Embed(
            title="Ranks",
            description="What is the highest rank you have achieved?",
            color=self.self.embedColor
        )

        #region Rank Buttons

        # Create the buttons
        button_ranks_GrandChampion = Button(
            style=discord.ButtonStyle.primary,
            label="Grand Champion",
            custom_id="grand_champion_button"
        )
        button_ranks_GrandChampion.callback = lambda i: button_callback(i, "Grand Champion")  # Use a lambda to pass the role name

        button_ranks_champion = Button(
            style=discord.ButtonStyle.primary,
            label="Champion",
            custom_id="champion_button"
        )
        button_ranks_champion.callback = lambda i: button_callback(i, "Champion")

        button_ranks_diamond = Button(
            style=discord.ButtonStyle.primary,
            label="Diamond",
            custom_id="diamond_button"
        )
        button_ranks_diamond.callback = lambda i: button_callback(i, "Diamond")

        button_ranks_platinum = Button(
            style=discord.ButtonStyle.primary,
            label="Platinum",
            custom_id="platinum_button"
        )
        button_ranks_platinum.callback = lambda i: button_callback(i, "Platinum")

        button_ranks_gold = Button(
            style=discord.ButtonStyle.primary,
            label="Gold",
            custom_id="gold_button"
        )
        button_ranks_gold.callback = lambda i: button_callback(i, "Gold")

        button_ranks_silver = Button(
            style=discord.ButtonStyle.primary,
            label="Silver",
            custom_id="silver_button"
        )
        button_ranks_silver.callback = lambda i: button_callback(i, "Silver")
        
        button_ranks_bronze = Button(
            style=discord.ButtonStyle.primary,
            label="Bronze",
            custom_id="Bronze_button"
        )
        button_ranks_bronze.callback = lambda i: button_callback(i, "Bronze")

        #endregion

        # Add the buttons to the rankEmbed
        rankView = View()
        rankView.add_item(button_ranks_GrandChampion)
        rankView.add_item(button_ranks_champion)
        rankView.add_item(button_ranks_diamond)
        rankView.add_item(button_ranks_platinum)
        rankView.add_item(button_ranks_gold)
        rankView.add_item(button_ranks_silver)
        rankView.add_item(button_ranks_bronze)

        await channel.send(embed=rankEmbed, view=rankView)
        print("Rank embed sent.")

        #endregion

        #region RegionEmbed

        regionEmbed = discord.Embed(
            title = 'Region',
            description= 'What region do you mostly play in?',
            color=self.self.embedColor
        )

        #region Region Buttons
        button_region_NA = Button(
            style=discord.ButtonStyle.primary,
            label="NA",
            custom_id="NA_button"
        )
        button_region_NA.callback = lambda i: button_callback(i, "NA")

        button_region_EU = Button(
            style=discord.ButtonStyle.primary,
            label="EU",
            custom_id="EU_button"
        )
        button_region_EU.callback = lambda i: button_callback(i, "EU")

        button_region_MENA = Button(
            style=discord.ButtonStyle.primary,
            label="MENA",
            custom_id="MENA_button"
        )
        button_region_MENA.callback = lambda i: button_callback(i, "MENA")

        button_region_OCE = Button(
            style=discord.ButtonStyle.primary,
            label="OCE",
            custom_id="OCE_button"
        )
        button_region_OCE.callback = lambda i: button_callback(i, "OCE")
        #endregion
        
        regionView = View()
        regionView.add_item(button_region_NA)
        regionView.add_item(button_region_EU)
        regionView.add_item(button_region_MENA)
        regionView.add_item(button_region_OCE)
        
        await channel.send(embed=regionEmbed, view=regionView)
        print("Region embed sent.")
        #endregion

        #region System/ConsoleEmbed

        platformEmbed = discord.Embed(
            title = 'System/Console',
            description= 'What system or console do you play on?',
            color=self.self.embedColor
        )

        #region Platform Buttons
        button_platform_PC = Button(
            style=discord.ButtonStyle.primary,
            label="PC",
            custom_id="pc_button"
        )
        button_platform_PC.callback = lambda i: button_callback(i, "PC")

        button_platform_Playstation = Button(
            style=discord.ButtonStyle.primary,
            label="Playstation",
            custom_id="playstation_button"
        )
        button_platform_Playstation.callback = lambda i: button_callback(i, "Playstation")

        button_platform_xbox = Button(
            style=discord.ButtonStyle.primary,
            label="Xbox",
            custom_id="xbox_button"
        )
        button_platform_xbox.callback = lambda i: button_callback(i, "Xbox")

        button_platform_switch = Button(
            style=discord.ButtonStyle.primary,
            label="Switch",
            custom_id="switch_button"
        )
        button_platform_switch.callback = lambda i: button_callback(i, "Switch")
        #endregion
        
        platformView = View()
        platformView.add_item(button_platform_PC)
        platformView.add_item(button_platform_Playstation)
        platformView.add_item(button_platform_xbox)
        platformView.add_item(button_platform_switch)
        
        await channel.send(embed=platformEmbed, view=platformView)
        print("Platform embed sent")
        #endregion

        #region LfgEmbed
        lfgEmbed = discord.Embed(
            title = 'Looking for friends roles',
            description= 'These roles are for if you want to be notified when others are looking for people to play with.',
            color=self.self.embedColor
        )

        #region Lfg Buttons
        button_lfg_competetive = Button(
            style=discord.ButtonStyle.primary,
            label="Competetive",
            custom_id="competetive_button"
        )
        button_lfg_competetive.callback = lambda i: button_callback(i, "Competetive")

        button_lfg_casual = Button(
            style=discord.ButtonStyle.primary,
            label="Casual",
            custom_id="casual_button"
        )
        button_lfg_casual.callback = lambda i: button_callback(i, "Casual")

        button_lfg_PrivateMatches = Button(
            style=discord.ButtonStyle.primary,
            label="Private matches",
            custom_id="privateMatches_button"
        )
        button_lfg_PrivateMatches.callback = lambda i: button_callback(i, "Private Matches")

        button_lfg_ExtraModes = Button(
            style=discord.ButtonStyle.primary,
            label="Extra Modes",
            custom_id="extraModes_button"
        )
        button_lfg_ExtraModes.callback = lambda i: button_callback(i, "Extra Modes")

        button_lfg_Tournaments = Button(
            style=discord.ButtonStyle.primary,
            label="Tournaments",
            custom_id="tournaments_button"
        )
        button_lfg_Tournaments.callback = lambda i: button_callback(i, "Tournaments")

        button_lfg_AlternateGames = Button(
            style=discord.ButtonStyle.primary,
            label="Alternate games",
            custom_id="alternateGames_button"
        )
        button_lfg_AlternateGames.callback = lambda i: button_callback(i, "Alternate games")

        #endregion

        lfgView = View()
        lfgView.add_item(button_lfg_competetive)
        lfgView.add_item(button_lfg_casual)
        lfgView.add_item(button_lfg_PrivateMatches)
        lfgView.add_item(button_lfg_ExtraModes)
        lfgView.add_item(button_lfg_Tournaments)
        lfgView.add_item(button_lfg_AlternateGames)
        
        await channel.send(embed=lfgEmbed, view=lfgView)
        print("Lfg embed sent")
        #endregion

        #region Additional roles Embed

        addRolesEmbed = discord.Embed(
            title = 'Additional Roles',
            description= 'These roles are specific interests that we offer in this discord! Choose any that you want to be a part of.',
            color=self.self.embedColor
        )

        #region Additional roles Buttons
        button_addRoles_CommunityEvents = Button(
            style=discord.ButtonStyle.primary,
            label="Community Events",
            custom_id="communityEvents_button"
        )
        button_addRoles_CommunityEvents.callback = lambda i: button_callback(i, "Community Events")

        button_addRoles_RLCS_Chat = Button(
            style=discord.ButtonStyle.primary,
            label="RLCS Chat",
            custom_id="rlcs_chat_button"
        )
        button_addRoles_RLCS_Chat.callback = lambda i: button_callback(i, "RLCS Chat")

        button_addRoles_Ladder = Button(
            style=discord.ButtonStyle.primary,
            label="1v1 Ladder",
            custom_id="ladder_button"
        )
        button_addRoles_Ladder.callback = lambda i: button_callback(i, "1v1 Ladder")

        button_addRoles_trading = Button(
            style=discord.ButtonStyle.primary,
            label="RL Trading",
            custom_id="trading_button"
        )
        button_addRoles_trading.callback = lambda i: button_callback(i, "RL Trading")
        
        button_addRoles_pc_HelpChat = Button(
            style=discord.ButtonStyle.primary,
            label="PC Help/Chat",
            custom_id="pcHelpChat_button"
        )
        button_addRoles_pc_HelpChat.callback = lambda i: button_callback(i, "PC Help/Chat")

        button_addRoles_musicChat = Button(
            style=discord.ButtonStyle.primary,
            label="Music Chat",
            custom_id="musicChat_button"
        )
        button_addRoles_musicChat.callback = lambda i: button_callback(i, "Music Chat")
        #endregion
        
        addRolesView = View()
        addRolesView.add_item(button_addRoles_CommunityEvents)
        addRolesView.add_item(button_addRoles_RLCS_Chat)
        addRolesView.add_item(button_addRoles_Ladder)
        addRolesView.add_item(button_addRoles_trading)
        addRolesView.add_item(button_addRoles_pc_HelpChat)
        addRolesView.add_item(button_addRoles_musicChat)

        await channel.send(embed=addRolesEmbed, view=addRolesView)
        print("Additional Roles embed sent")
        
        #endregion


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))