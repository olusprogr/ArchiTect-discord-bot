import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from database._databaseManager import *
import asyncio
import json


class Suggest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delay = 0

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]
        userDB = data["databases"]["preferredUser"]

        self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    @slash_command(description="Suggest something in a thread")
    @discord.default_permissions(create_public_threads=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest(self, ctx,
                      suggestions: str,
                      duration: Option(float, choices=[
                          60, 1440, 4320, 10080
                      ]),
                      rules: Option(str, default=None),
                      slowmode_delay: Option(int, choices=[
                          0, 5, 10, 15, 30, 60, 120,
                      ], default=None)
                   ):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), suggestions)

        if slowmode_delay is None: slowmode_delay = 5

        await ctx.respond("Creating a thread for your suggestion...", ephemeral=True, delete_after=3)
        message = await ctx.send(suggestions)
        await asyncio.sleep(1)

        thread_name = suggestions[:99]

        embed = discord.Embed(
            title="Created thread using /suggest command",
            description=f"**Content**: {thread_name}",
            color=0x674CBB
        )
        if rules: embed.add_field(name="**Rules**", value=rules)
        embed.add_field(name="Settings for this thread/discussion",
                        value=f"Thread duration:\n"
                              f"{round(duration / 60, 1)}hours | "
                              f"{round(duration / 60 / 24, 2)}days"
                        )

        thread = await message.create_thread(name=suggestions, auto_archive_duration=duration)
        await thread.edit(slowmode_delay=slowmode_delay)
        await thread.send(embed=embed)


    @suggest.error
    async def suggest_error(self, ctx, error):
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
            embed.description = "I don't have the necessary permissions to send messages in the specified channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = "An unknown error occurred."
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Suggest(bot))
