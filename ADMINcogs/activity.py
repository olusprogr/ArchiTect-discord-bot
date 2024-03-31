import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from database._databaseManager import *
import json


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]
        userDB = data["databases"]["preferredUser"]

        self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    activity1 = SlashCommandGroup("activity", description="Activity group")

    @activity1.command(description="Set the Bots activity")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def change(
            self, ctx,
            status: Option(str, choices=["Online", "Do not disturb", "Idle", "Invisible"]),
            name: Option(str),
    ):

        asw = self.check.checkForPremium(ctx.author.id, "user")
        asw2 = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{status}, {name}")

        if asw and asw2:
            act = discord.Game(name=name)
            status1 = None

            if status == "Online":
                status1 = discord.Status.online
            if status == "Do not disturb":
                status1 = discord.Status.do_not_disturb
            if status == "Idle":
                status1 = discord.Status.idle
            elif status == "Invisible":
                status1 = discord.Status.invisible

            await self.bot.change_presence(activity=act, status=status1)
            await ctx.respond("Status has been changed!", ephemeral=True, delete_after=3)
        else:
            await ctx.respond("You don't own the ArchiTect Premium version of the bot.", ephemeral=True, delete_after=5)

    @change.error
    async def change_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Please provide valid arguments."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, discord.DiscordException):
            embed.description = f"An error occurred: {error}"

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    # --------------------------------------------------------

    @activity1.command(description="Set the Bots activity to default settings")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def default(self, ctx):
        asw = self.check.checkForAdmin(ctx.author.id, "user")
        asw2 = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        if asw and asw2:
            await self.bot.change_presence()
            await ctx.respond("Status has been changed to the default!", ephemeral=True, delete_after=3)
        else:
            await ctx.respond("You don't own the ArchiTect Premium version of the bot.", ephemeral=True, delete_after=5)

    @change.error
    async def change_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, discord.DiscordException):
            embed.description = f"An error occurred: {error}"

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Activity(bot))
