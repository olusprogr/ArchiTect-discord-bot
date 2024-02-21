import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option

from database._databaseManager import *

import json


class Password(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?&%$_'

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    create = SlashCommandGroup(name="create", description="Create group")

    @create.command(name="password", description="Create a secure password!")
    @discord.option("lenght", int, description="Select a password lenght (mind. 6 - max 32 characters)", required=True)
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def password(self, ctx, lenght: Option(int, "Select the lenght of your password", min_value=6, max_value=32)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{lenght}")

        password = ''.join(random.choice(self.chars) for i in range(lenght))
        embed = discord.Embed(color=0xC87A80, title="",
                              description=f"Your password is: ||{password}||")
        await ctx.respond(embed=embed,  delete_after=30, ephemeral=True)

    @password.error
    async def password_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to send messages in this channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        elif isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred while executing the command: {error.original}"

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Password(bot))