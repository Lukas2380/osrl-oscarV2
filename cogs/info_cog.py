import json
import discord
from discord.ext import commands
from discord import app_commands, TextChannel
from data.helper_functions import *
    
class Info_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_ids = {}
        self.footerText = "Thank you for being a part of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you"
        
        # Load roles config in initialization
        self.load_roles_config()
        
        # Fetch channel IDs asynchronously after initialization
        bot.loop.create_task(self.fetch_channel_ids())

    async def fetch_channel_ids(self):
        try:
            response = infoChannelsTable.select("channel_id", "channel_name").execute()
            self.channel_ids = {record["channel_name"]: record["channel_id"] for record in response.data}
        except Exception as e:
            print(e)

    def load_roles_config(self):
        try:
            with open('./data/info/roles_config.json', 'r') as file:
                self.roles_config = json.load(file)
        except Exception as e:
            print(e)

    async def save_channel_ids(self):
        try:
            for channel_name, channel_id in self.channel_ids.items():
                infoChannelsTable.update({"channel_id": channel_id}).eq("channel_name", channel_name).execute()
        except Exception as e:
            print(e)

    @app_commands.command(name="info-setchannels", description="Set channels for the info embeds")
    async def set_channels(self, interaction: discord.Interaction, rules: TextChannel, faq: TextChannel, anonrep: TextChannel, servdir: TextChannel, servstaff: TextChannel, ladderrules: TextChannel, ladderadmininfo: TextChannel, ladderinfo: TextChannel, roles: TextChannel):
        await interaction.response.defer()
        self.channel_ids = {
            "servrules": rules.id,
            "faq": faq.id,
            "anonrep": anonrep.id,
            "servdir": servdir.id,
            "servstaff": servstaff.id,
            "1v1rules": ladderrules.id,
            "admininfo": ladderadmininfo.id,
            "1v1info": ladderinfo.id,
            "rolesintro": roles.id
        }
        
        # Save channel IDs to the database
        await self.save_channel_ids()
        await interaction.followup.send("Channels have been set.")

    @app_commands.command(name="info-send", description="Resends one of the information embeds to the selected channel.")
    async def info_send(self, interaction, info: typing.Literal["1v1info", "1v1rules", "admininfo", "anonrep", "coaching", "faq", "rlconnect", "rolesintro", "servrules", "servstaff", "tmsearch", "welcome"]):
        
        
        return

    @app_commands.command(name="info-servrules", description="Resend the rules embed")
    async def servrules(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("rulesChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))

        channel = self.bot.get_channel(channel_id)
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

    @app_commands.command(name="info-servfaq", description="Resend the FAQ embed")
    async def servfaq(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("faqChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def servanonrep(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("anonrepChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def servdir(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("servdirChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
        await channel.purge(limit=1)
        
        with open('./data/info/servdir.txt', 'r') as file:
            servdir = file.read()
        
        servdirec = discord.Embed(title='Old School Server Directory', description=servdir, color=infoEmbedColor)
        servdirec.set_footer(text=self.footerText)
        await channel.send(embed=servdirec)
        response = discord.Embed(title='Embed Sent')
        await interaction.followup.send(embed=response)

    @app_commands.command(name="info-servstaff", description="Resend the server staff embed")
    async def servstaff(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("servstaffChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def ladderrules(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("ladderrulesChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def ladderadmininfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("ladderadmininfoChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def ladderinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("ladderinfoChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))
        
        channel = self.bot.get_channel(channel_id)
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
    async def rolesembed(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = self.channel_ids.get("rolesChannel")
        if not channel_id:
            return await interaction.followup.send(embed=discord.Embed(title="Error", description="No channel for this embed selected, please use the /setchannels command."))

        channel = self.bot.get_channel(channel_id)
        await channel.purge(limit=6)

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
            if channel_id != self.channel_ids.get("rolesChannel"):
                return

            message_id = payload.message_id
            channel = discord.utils.find(lambda c: c.id == channel_id, guild.text_channels)
            message = await channel.fetch_message(message_id)

            if message.author.id == self.bot.user.id:
                emoji = payload.emoji.name
                member = guild.get_member(payload.user_id)

                if not member.bot:
                    for _, data in self.roles_config.items():
                        roles = data.get("roles", {})
                        if emoji in roles.values():
                            role_name = next(role for role, role_emoji in roles.items() if role_emoji == emoji)
                            role = discord.utils.get(guild.roles, name=role_name)

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
