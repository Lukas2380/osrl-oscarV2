from io import BytesIO
import io
import typing
import discord
from discord import Color, Embed, app_commands
from discord.ext import commands
import json
import random
import os

class RocketLeagueItems(commands.Cog):
    crate_names = []

# Define a dictionary to map paint names to hex color values
    paint_colors = {
        "Black": 0x1B1B1B,
        "Burnt Sienna": 0x8C4A2E,
        "Cobalt": 0x0033CC,
        "Crimson": 0xDC143C,
        "Forest Green": 0x228B22,
        "Gold": 0xFFD700,
        "Grey": 0x808080,
        "Lime": 0x00FF00,
        "Orange": 0xFFA500,
        "Pink": 0xFF69B4,
        "Purple": 0x800080,
        "Saffron": 0xF4C430,
        "Sky Blue": 0x87CEEB,
        "Titanium White": 0xFFFFFF
    }

    paint_blocks = {
        "Black": "⬛",                  # Dark black square
        "Burnt Sienna": "🟫",           # Brown square for Burnt Sienna
        "Cobalt": "🟦",                 # Dark blue square
        "Crimson": "🟥",                # Red square for Crimson
        "Forest Green": "🌲",           # Tree emoji for a darker green look
        "Gold": "⭐",                   # Star emoji for Gold to differentiate from Saffron
        "Grey": "⬜",                   # Light grey square
        "Lime": "🟩",                   # Bright green for Lime
        "Orange": "🟧",                 # Orange square for Orange
        "Pink": "🌸",                   # Cherry blossom for a lighter pink
        "Purple": "🟪",                 # Purple square for Purple
        "Saffron": "🟨",                # Yellow square for Saffron
        "Sky Blue": "🔹",               # Light blue diamond for Sky Blue
        "Titanium White": "⬜"          # White square for Titanium White
    }

    def __init__(self, bot):
        self.bot = bot
        self.crates = self.load_crates()  # Load crate data from JSON file
        self.user_inventories = self.load_inventories()  # Load user inventory data from JSON file
        self.crate_names = list(self.crates.keys())

    def load_crates(self):
        """Load crate data from a JSON file."""
        with open("./data/rocketLeagueItems/crates.json", "r") as file:
            return json.load(file)

    def load_inventories(self):
        """Load user inventories from a JSON file."""
        with open("./data/rocketLeagueItems/inventories.json", "r") as file:
            return json.load(file)
        return {}

    def save_inventories(self):
        """Save user inventories to a JSON file."""
        with open("./data/rocketLeagueItems/inventories.json", "w") as file:
            json.dump(self.user_inventories, file, indent=4)

    def get_item(self, crate_name):
        # Define drop rate thresholds
        rarity_rates = {
            "Rare": 55,
            "Very Rare": 28,
            "Import": 12,
            "Exotic": 4,
            "Black Market": 1
        }

        # Paint and certification chances
        paint_chance = 25  # 25% chance for paint
        cert_chance = 25   # 25% chance for certification

        # All available certifications
        certifications = [
            "Acrobat", "Aviator", "Goalkeeper", "Guardian", "Juggler", 
            "Paragon", "Playmaker", "Scorer", "Show-Off", "Sniper", 
            "Striker", "Sweeper", "Tactician", "Turtle", "Victor"
        ]

        # Determine rarity based on drop rates
        rarity_roll = random.uniform(0, 100)
        cumulative = 0
        rarity = "Rare"  # Default rarity

        for r, rate in rarity_rates.items():
            cumulative += rate
            if rarity_roll <= cumulative:
                rarity = r
                break

        # Select a random item from the determined rarity category
        random_item_index = random.randint(0, len(self.crates[crate_name][rarity]) - 1)
        item = self.crates[crate_name][rarity][random_item_index]

        # Get possible paints for the item
        paints = item.get("Paints", None)

        # Determine if the item is painted
        painted = random.uniform(0, 100) < paint_chance
        paint = random.choice(paints) if painted and paints else None

        # Determine if the item is certified
        certified = random.uniform(0, 100) < cert_chance
        cert = random.choice(certifications) if certified else None

        # Prepare the Versions dictionary
        item_versions = {
            "Rarity": rarity,
            "Paint": paint,
            "Certification": cert,
            "Crate": crate_name
        }

        # Remove the "Paints" key if it exists
        if "Paints" in item:
            del item["Paints"]

        # Attach the Versions dictionary to the item
        item["Versions"] = [item_versions]

        return item


    async def crates_autocomplete(
        self, 
        interaction: discord.Interaction, 
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        # If no input, return the first 25 items
        if not current:
            return [
                app_commands.Choice(name=crate, value=crate)
                for crate in self.crate_names[:25]  # Only show the first 25 items
            ]
        
        # If there is input, filter the list and limit to 25 items
        filtered_crates = [
            crate for crate in self.crate_names if current.lower() in crate.lower()
        ]
        return [
            app_commands.Choice(name=crate, value=crate)
            for crate in filtered_crates[:25]  # Limit to 25 items after filtering
        ]

    @app_commands.command(name="opencrate", description="Open a crate and receive a random item.")
    @app_commands.autocomplete(crate_name=crates_autocomplete)
    async def open_crate(self, interaction: discord.Interaction, crate_name: str):
        await interaction.response.defer()

        # Check if the crate exists in loaded data
        if crate_name not in self.crates:
            response = Embed(
                title="Crate Not Found",
                description=f"The crate '{crate_name}' does not exist. Please check the name.",
                color=Color.red()
            )
            await interaction.followup.send(embed=response)
            return

        # Get item with attributes included
        item = self.get_item(crate_name)

        # Add item to user inventory and save the update
        user_id = str(interaction.user.id)

        # Ensure the user inventory exists
        if user_id not in self.user_inventories:
            self.user_inventories[user_id] = {"Items": [], "Preset": {}}

        # Check if the item exists in the inventory
        inventory_items = self.user_inventories[user_id]["Items"]
        existing_item = next(
            (inv_item for inv_item in inventory_items 
            if inv_item["Name"] == item["Name"] and 
                inv_item.get("Type") == item.get("Type") and 
                inv_item.get("RequiredBody") == item.get("RequiredBody")),
            None
        )

        currentVersion = item["Versions"][0]

        if existing_item:
            # Get the first version from the item (assuming we're working with one version at a time)
            matching_version = next(
                (version for version in existing_item["Versions"]
                if version["Rarity"] == currentVersion["Rarity"] and
                    version["Paint"] == currentVersion["Paint"] and
                    version["Certification"] == currentVersion["Certification"] and
                    version["Crate"] == currentVersion["Crate"]),
                None
            )

            if matching_version:
                # Increment duplicates if the version exists
                matching_version["Duplicates"] = matching_version.get("Duplicates", 1) + 1
            else:
                # Add a new version if it doesn't exist
                existing_item["Versions"].append(currentVersion)
        else:
            # Add the item as a new entry in the inventory
            inventory_items.append(item)

        # Save updated inventory
        self.save_inventories()

        response = Embed()

        # Prepare attributes for the embed
        attributeText = " "
        if currentVersion["Paint"]:
            attributeText = str(currentVersion["Paint"]) + ' '
            paint_block = self.paint_blocks.get(currentVersion["Paint"], "")
            response.add_field(name="Paint", value=f"{paint_block} {currentVersion['Paint']}", inline=True)
        if currentVersion["Certification"]:
            attributeText += str(currentVersion["Certification"]) + ' '
            response.add_field(name="Certification", value=currentVersion["Certification"], inline=True)

        # Get color from the paint color dictionary or default to green
        embed_color = self.paint_colors.get(currentVersion["Paint"], 0x292929)  # Default to 0x292929FF

        response.color = embed_color
        response.description = f"Crate: **{crate_name}** Opened!"
        response.title = f"You received: **{attributeText}'{item['Name']}'**!"

        # Add item attributes to the embed
        response.add_field(name="", value="", inline=False)
        response.add_field(name="Item", value=item["Name"], inline=True)
        response.add_field(name="Type", value=item.get("Type", "/"), inline=True)
        response.add_field(name="Vehicle", value=item.get("RequiredBody", "All"), inline=True)

        await interaction.followup.send(embed=response)


    @app_commands.command(name="inventory", description="Check your inventory.")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        inventory = self.user_inventories.get(user_id, {}).get("Items", [])
        
        if not inventory:
            response = discord.Embed(
                title="Inventory Empty",
                description="Your inventory is currently empty. Try opening a crate!",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=response)
            return

        # Organize inventory by crate
        crate_dict = {}
        for item in inventory:
            for version in item["Versions"]:
                crate = version.get("Crate", "Unknown")
                if crate not in crate_dict:
                    crate_dict[crate] = []
                
                # Append item details to the corresponding crate
                crate_dict[crate].append({
                    "Name": item["Name"],
                    "Type": item["Type"],
                    "RequiredBody": item.get("RequiredBody", "None"),
                    "Rarity": version["Rarity"],
                    "Paint": version.get("Paint", "None"),
                    "Certification": version.get("Certification", "None"),
                    "Duplicates": version.get("Duplicates", "/")
                })

        # Create the text file content
        output_lines = []
        for crate, items in sorted(crate_dict.items()):
            output_lines.append(f"=== {crate.upper()} ===")
            for item in items:
                output_lines.append(
                    f"- {item['Name']} ({item['Type']})\n"
                    f"  Required Body: {item['RequiredBody']}\n"
                    f"  Rarity: {item['Rarity']}, Paint: {item['Paint']}, Certification: {item['Certification']}, Duplicates: {item['Duplicates']}\n"
                )
            output_lines.append("")  # Blank line between crates

        # Create a file in memory
        inventory_file = io.StringIO("\n".join(output_lines))
        inventory_file.seek(0)

        # Send the file
        await interaction.followup.send(
            content="Here is your inventory, sorted by crate:",
            file=discord.File(fp=inventory_file, filename="inventory.txt")
        )



    @app_commands.command(name="equip", description="Equip an item to your preset.")
    async def equip(self, interaction: discord.Interaction, item_type: str, item_name: str):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        inventory = self.user_inventories.get(user_id, {}).get("items", [])
        
        if item_name not in inventory:
            response = discord.Embed(
                title="Item Not Found",
                description=f"You don't have **{item_name}** in your inventory.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=response)
            return

        # Equip the item in the preset and save the update
        self.user_inventories[user_id]["preset"][item_type] = item_name
        self.save_inventories()  # Save the updated preset

        response = discord.Embed(
            title="Item Equipped",
            description=f"Equipped **{item_name}** as your {item_type}.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=response)

    @app_commands.command(name="preset", description="Display your current equipped preset.")
    async def preset(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        preset = self.user_inventories.get(user_id, {}).get("preset", {})

        if not preset:
            response = discord.Embed(
                title="Preset Empty",
                description="You haven't equipped any items yet.",
                color=discord.Color.orange()
            )
        else:
            preset_items = "\n".join(f"{slot}: {item}" for slot, item in preset.items())
            response = discord.Embed(
                title="Your Current Preset",
                description=preset_items,
                color=discord.Color.blue()
            )
        
        await interaction.followup.send(embed=response)

    @app_commands.command(name="crateinfo", description="Get details on what items a crate contains.")
    async def crate_info(self, interaction: discord.Interaction, crate_name: str):
        await interaction.response.defer()
        
        if crate_name not in self.crates:
            response = discord.Embed(
                title="Crate Not Found",
                description=f"The crate '{crate_name}' does not exist. Please check the name.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=response)
            return
        
        items = "\n".join(self.crates[crate_name])
        response = discord.Embed(
            title=f"Items in {crate_name}",
            description=items,
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=response)

    @app_commands.command(name="trade", description="Trade an item with another user.")
    async def trade(self, interaction: discord.Interaction, user: discord.User, item_name: str):
        await interaction.response.defer()

        response = discord.Embed(
            title="Trade Feature",
            description=f"Trading **{item_name}** with {user.mention}.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=response)

    @app_commands.command(name="stats", description="View your crate-opening and item stats.")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        response = discord.Embed(
            title="Your Stats",
            description="Here are your crate-opening and item stats.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=response)

# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(RocketLeagueItems(bot))
