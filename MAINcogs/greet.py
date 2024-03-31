import random

import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from database._databaseManager import *

import json


class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Greet a user of your choice")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def greet(self, ctx,
                    user: Option(discord.User, "The user you want to greet")):

        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{user}")

        greetings = [
            f"Hi {user.mention}! 👋",
            f"Hello {user.mention}! 😊",
            f"Greetings, {user.mention}! 🌟",
            f"Howdy {user.mention}! 🤠",
            f"Hey there {user.mention}! 😄",
            f"A warm welcome, {user.mention}! 😃",
            f"Hiya {user.mention}! 🌺",
            f"Glad to see you, {user.mention}! 😁",
            f"Salutations {user.mention}! 🌍"
        ]

        if registerOperation: await ctx.respond(random.choice(greetings))

    @greet.error
    async def greet_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error:")

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided. Make sure you mention a valid user."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Greet(bot))