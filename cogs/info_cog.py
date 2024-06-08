import json
import sys
import discord
from discord.ext import commands
from discord import app_commands, TextChannel
from discord.ui import View, Button
from data.helper_functions import *

infochannelsTable = supabase.schema("info_tables").table("InfoChannels")


class Info_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Fetch the channel IDs from the InfoChannels table
    response = infochannelsTable.select("channel_id").execute()
    channel_ids = [record["channel_id"] for record in response.data]
    rulesChannel, faqChannel, anonrepChannel, servdirChannel, servstaffChannel, ladderrulesChannel, ladderadmininfoChannel, ladderinfoChannel, rolesChannel = channel_ids[:9]

    footerText = "Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you"

    with open('./data/info/roles_config.json', 'r') as file:
        try:
            roles_config = json.load(file)
        except Exception as e:
            print(e)

    def save_channel_ids(self):
        # Mapping of channel names to their respective IDs
        channels_data = {
            "rulesChannel": self.rulesChannel,
            "faqChannel": self.faqChannel,
            "anonrepChannel": self.anonrepChannel,
            "servdirChannel": self.servdirChannel,
            "servstaffChannel": self.servstaffChannel,
            "ladderrulesChannel": self.ladderrulesChannel,
            "ladderadmininfoChannel": self.ladderadmininfoChannel,
            "ladderinfoChannel": self.ladderinfoChannel,
            "rolesChannel": self.rolesChannel,
        }

        # Update each channel's ID in the database
        try:
            for channel_name, channel_id in channels_data.items():
                infochannelsTable.update({"channel_id": channel_id}).eq("channel_Name", channel_name).execute()
        except Exception as e:
            print(e)

    @app_commands.command(name="info-setchannels", description="Set channels for the info embeds")
    async def set_channels(self, interaction, rules: TextChannel, faq: TextChannel, anonrep: TextChannel, servdir: TextChannel, servstaff: TextChannel, ladderrules: TextChannel, ladderadmininfo: TextChannel, ladderinfo: TextChannel, roles: TextChannel):
        await interaction.response.defer()
        self.rulesChannel = rules.id
        self.faqChannel = faq.id
        self.anonrepChannel = anonrep.id
        self.servdirChannel = servdir.id
        self.servstaffChannel = servstaff.id
        self.ladderrulesChannel = ladderrules.id
        self.ladderadmininfoChannel = ladderadmininfo.id
        self.ladderinfoChannel = ladderinfo.id
        self.rolesChannel = roles.id

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
        
        with open('./data/info/welcome.txt', 'r') as file:
            welcome = file.read()
        with open('./data/info/rlconnect.txt', 'r') as file:
            rlconnect = file.read()
        with open('./data/info/tmsearch.txt', 'r') as file:
            tmsearch = file.read()
        with open('./data/info/coaching.txt', 'r') as file:
            coaching = file.read()
        servdirec = discord.Embed(title='Old School Server Directory', color=infoEmbedColor)
        servdirec.add_field(name='Welcome', value=welcome, inline=False)
        servdirec.add_field(name='RL Connect', value=rlconnect, inline=False)
        servdirec.add_field(name='Teammate Search', value=tmsearch, inline=False)
        servdirec.add_field(name='Coaches Corner', value=coaching, inline=False)
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

    @app_commands.command(name="info-rolesembed", description="Resend the roles embed")
    async def rolesembed(self, interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(self.rolesChannel)
        if not channel:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))

        await channel.purge(limit=6)

        #region RolesIntroEmbed
        with open('./data/info/rolesintro.txt', 'r') as file:
            rolesintro = file.read()

        rolesIntroEmbed = discord.Embed(
            title='Assign your roles',
            description=rolesintro,
            color=infoEmbedColor
        )

        await channel.send(embed=rolesIntroEmbed)
        await log("--- Rolesintro embed sent.")

        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)
        #endregion

        for category, data in self.roles_config.items():
            title = data["title"]
            description = data["description"]
            roles = data.get("roles", {})

            # Create an embed
            rolesEmbed = discord.Embed(
                title=title,
                description=description,
                color=infoEmbedColor
            )
            sent_message = await channel.send(embed=rolesEmbed)

            # Add reactions based on roles
            await self.add_custom_reactions(sent_message, roles.values(), interaction.guild)
            await log(f"--- {category} embed sent.")

    async def add_custom_reactions(self, sent_message, emoji_names, guild):
        for emoji_name in emoji_names:
            custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
            if custom_emoji:
                try:
                    await sent_message.add_reaction(custom_emoji)
                except Exception as e:
                    await log(e)
            else:
                await log(f"Custom emoji '{emoji_name}' not found.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.handle_reaction(payload, add=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.handle_reaction(payload, add=False)

    async def handle_reaction(self, payload, add=True): 
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)

        if guild:
            channel_id = payload.channel_id
            channel = discord.utils.find(lambda c: c.id == channel_id, guild.text_channels)

            if channel and channel_id == self.rolesChannel:
                message_id = payload.message_id
                message = await channel.fetch_message(message_id)
                
                # Check if the reaction is added/removed from a message sent by your bot
                if message.author.id == self.bot.user.id:
                    # Handle the reaction based on the emoji
                    emoji = payload.emoji.name
                    member = guild.get_member(payload.user_id)

                    # Check if the user is not a bot
                    if not member.bot:
                        # Check which category the emoji belongs to
                        for _, data in self.roles_config.items():
                            roles = data.get("roles", {})
                            if emoji in roles.values():
                                # Find the role associated with the emoji
                                role_name = next(role for role, role_emoji in roles.items() if role_emoji == emoji)
                                
                                # Get the role object from the guild
                                role = discord.utils.get(guild.roles, name=role_name)

                                # Add or remove the role from the member based on the 'add' parameter
                                if role:
                                    if add:
                                        await member.add_roles(role)
                                        await log(f"--- Added role {role_name} to {member.display_name}")
                                    else:
                                        await member.remove_roles(role)
                                        await log(f"--- Removed role {role_name} from {member.display_name}")
                                    break
                                else:
                                    await log(f"Role {role_name} not found", error=True)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Info_Cog(bot))