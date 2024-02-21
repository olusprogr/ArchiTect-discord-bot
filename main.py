import time
start_time = time.time()
import os
from dotenv import load_dotenv
import psutil

import discord
#from debug.ADMIN import Database, Log, Administrator

# Setting up the bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Setting up the bot status and activity
status = discord.Status.dnd
activity = discord.Activity(type=discord.ActivityType.playing, name="Booting...")

bot = discord.Bot(
    intents=intents,
    activity=activity,
    status=status
)


# Function to get the current time
def getCurrentTime():
    t = time.localtime()
    current_time = time.asctime(t)
    return current_time


# Initialising all the extensions
if __name__ == "__main__":
    count = 1
    cog_directories = ["MAINcogs", "ADMINcogs", "PREMIUMcogs", "ADDITIONALS"]

    for cog_directory in cog_directories:
        for filename in os.listdir(cog_directory):
            if filename.endswith(".py"):
                cog_path = os.path.join(cog_directory, filename)
                bot.load_extension(f"{cog_directory}.{filename[:-3]}")
                print(f"- {count} {cog_path} loaded!")
                count += 1
                
    # Additional initialisations
    # Administrator(Database("databases/user.db")).createTable("user")
    # Administrator(Database("user.db")).write("olus.test", "1145981840071606312", 0, 1)
    # Log(Database("databases/log.db")).createTable("log")


# Event to run when the bot is ready
@bot.event
async def on_ready():
    # Getting the bot's stats and performance
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_info = psutil.virtual_memory()
    total_ram = round(ram_info.total / (1024 ** 3), 2)
    available_ram = round(ram_info.available / (1024 ** 3), 2)
    used_ram = round(ram_info.used / (1024 ** 3), 2)

    end_time = time.time()
    boot_time = end_time - start_time

    # Printing whenever the bot is ready
    print(
        f"Bot booted in {boot_time:.2f} seconds\n"
        f"Name: {bot.user}\n"
        f"Description: {bot.description if bot.description is None else 'Empty'}\n"
        f"Invite: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands\n"
        f"Bot ID: {bot.user.id}\n"
        f"Server count: {len(bot.guilds)}\n"
        f"Ping: {int(bot.latency * 1000)}ms\n\n"
        f"CPU-usage: {cpu_usage}%\n"
        f"Total RAM: {total_ram} GB\n"
        f"Available RAM: {available_ram} GB\n"
        f"Used RAM: {used_ram} GB\n\n"
        f"{bot.user} marked as running..."
    )

    channel = await bot.fetch_channel(1167786310682034246)
    await channel.send(f"{getCurrentTime()}: {bot.user.mention} marked as running...")

    # Changing the bot's status and activity
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(type=discord.ActivityType.listening,
                                                        name=f" {len(bot.guilds)} server"))


# Loading the token from the .env file
load_dotenv()
bot.run(os.getenv("TOKEN"))