import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random
import os

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

collectibles_folder = "./collectibles"
collectible_files = [f for f in os.listdir(collectibles_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Track active channels
active_channels = {}

# Background loop
@tasks.loop(seconds=60)
async def summon_characters():
    for guild_id, channel in active_channels.items():
        # Random interval check
        if random.random() < 0.25:  # approx 1-in-4 chance per minute
            if collectible_files:
                chosen = random.choice(collectible_files)
                file = discord.File(f"{collectibles_folder}/{chosen}", filename="collectible.png")
                embed = discord.Embed(title="✨ A collectible appeared!", color=0xffbb00)
                embed.set_image(url="attachment://collectible.png")

                button = discord.ui.Button(label="Catch me!", style=discord.ButtonStyle.success)

                async def button_callback(interaction):
                    await interaction.response.send_message("You caught it!", ephemeral=True)

                button.callback = button_callback
                view = discord.ui.View()
                view.add_item(button)

                try:
                    await channel.send(embed=embed, file=file, view=view)
                except Exception as e:
                    print(f"Failed to send in {guild_id}: {e}")

@bot.event
async def on_ready():
    await tree.sync()
    summon_characters.start()
    print(f"MyDex online as {bot.user}")

# Slash command to start MyDex in a channel
@tree.command(name="startme", description="Activate MyDex in this channel.")
async def startme(interaction: discord.Interaction):
    active_channels[interaction.guild.id] = interaction.channel
    await interaction.response.send_message("✅ MyDex is now active in this channel! Watch for collectibles every few minutes.")

bot.run("DISCORD_TOKEN")
