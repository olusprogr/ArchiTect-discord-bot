import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json
from ping3 import ping

async def ping_website(adress: str) -> float: # to fix
    return round(ping(adress) * 1000, 1)


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Get the bots ping")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ping(self, ctx):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command))
        redditPing = await ping_website("www.reddit.com")
        steamAPI = await ping_website("store.steampowered.com")

        embed = discord.Embed(title="🏓PONG/LATENCY🏓", color=0xC87A80)
        embed.add_field(name="Client latency", value=f"**{round(self.bot.latency * 1000, 1)}ms**")
        embed.add_field(name="Reddit API", value=f"**{redditPing}ms**")
        embed.add_field(name="Steam API", value=f"**{steamAPI}ms**")
        embed.set_footer(text="Issues on discords or the API-provider sides could create weird or high latency.")
        if registerOperation: await ctx.respond(embed=embed)

    @ping.error
    async def bot_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred while executing the command: {error.original}"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to send messages in this channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = "An unknown error occurred."
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

def setup(bot):
    bot.add_cog(Ping(bot))
