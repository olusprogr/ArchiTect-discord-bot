import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from database._databaseManager import *

import json


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Clear messages in your selected textchannel")
    @discord.default_permissions(manage_messages=True)
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def clear(self, ctx,
                    amount: Option(int, min_value=1, max_value=100),
                    channel: Option(discord.TextChannel, required=False)
                    ):

        if channel is None: channel = ctx.channel
        await ctx.defer(ephemeral=True)

        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{amount}, {channel}")
        if registerOperation:
            embed = discord.Embed(color=0xC87A80, title="Output:",
                                  description=f"Deleting {amount} messages in channel: {channel}...\n"
                                              f"Please be patient for a moment.\nThis may take some time.")
            await ctx.respond(embed=embed, ephemeral=True, delete_after=10)
            await channel.purge(limit=amount)

    @clear.error
    async def clear_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, commands.CheckFailure):
            embed.description = "You don't have the necessary permissions to use this command."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to manage messages in the specified channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Clear(bot))
