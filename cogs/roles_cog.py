import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rolesembed", description="roles embed")
    async def rolesembed(self, interaction):
        print("Command invoked.")

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
                await interaction.send(f"Role operation completed for {user.mention}. Check your DMs for details.", ephemeral=True)
            else:
                print("Role not found.")
                await interaction.send("Role not found. Please contact an administrator.")

        #region RolesIntroEmbed

        with open('./data/rolesintro.txt', 'r') as file:
            rolesintro = file.read()

        rolesIntroEmbed = discord.Embed(
            title = 'Assign your roles',
            description=rolesintro,
            color=0x2ddaed
        )

        await interaction.response.send_message(embed=rolesIntroEmbed)
        print("Rolesintro embed sent.")

        #endregion

        #region RankEmbed

        # Create an embed
        rankEmbed = discord.Embed(
            title="Ranks",
            description="What is the highest rank you have achieved?",
            color=discord.Color.blue()
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

        await interaction.followup.send(embed=rankEmbed, view=rankView)
        print("Rank embed sent.")

        #endregion

        #region RegionEmbed

        regionEmbed = discord.Embed(
            title = 'Region',
            description= 'What region do you mostly play in?',
            color=discord.Color.blue()
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
        
        await interaction.followup.send(embed=regionEmbed, view=regionView)
        print("Region embed sent.")
        #endregion

        #region System/Console

        platformEmbed = discord.Embed(
            title = 'System/Console',
            description= 'What system or console do you play on?',
            color=discord.Color.blue()
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
        
        await interaction.followup.send(embed=platformEmbed, view=platformView)
        print("Platform embed sent")
        #endregion

        #region Lfg
        lfgEmbed = discord.Embed(
            title = 'Looking for friends roles',
            description= 'These roles are for if you want to be notified when others are looking for people to play with.',
            color=discord.Color.blue()
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
        
        await interaction.followup.send(embed=lfgEmbed, view=lfgView)
        print("Lfg embed sent")
        #endregion

        #region Additional roles

        addRolesEmbed = discord.Embed(
            title = 'Additional Roles',
            description= 'These roles are specific interests that we offer in this discord! Choose any that you want to be a part of.',
            color=discord.Color.blue()
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

        await interaction.followup.send(embed=addRolesEmbed, view=addRolesView)
        print("Additional Roles embed sent")

        #endregion

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolesCog(bot))