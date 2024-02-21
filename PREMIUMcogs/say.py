import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from database._databaseManager import Database, Log, Administrator
import json


class DatabaseEntryDecorator:
    def __init__(self, DB):
        self.log_db = DB

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            guild = str(args[0].guild) if args and args[0].guild else "None"
            author = str(args[0].author) if args and args[0].author else "None"
            command = str(args[0].command) if args and args[0].command else "None"
            add_conent = f"{args[1]}, {args[2]}" if args and len(args) > 2 else "None"

            asw = self.log_db.log(guild, author, command, add_conent)
            print(asw)
            if asw:
                output = func(*args, **kwargs); return output
            return None

        return wrapper


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delay = 0

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

            logDB = data["databases"]["savingUserOperations"]
            userDB = data["databases"]["preferredUser"]

        self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    @slash_command(description="Let the Bot write something for you")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def say(self, ctx,
                  text: Option(str, "Don't user the symbol [@]"),
                  channel: Option(discord.TextChannel, "Select the channel you want to send in", default=None)
                  ):

        if channel is None: channel = ctx.channel
        @DatabaseEntryDecorator(self.log_DB)
        def trigger(*args, **kwargs) -> None: pass
        trigger(ctx, text, channel)

        if self.check.checkForPremium(ctx.author.id, "user"):
            await ctx.respond("Here you go", ephemeral=True, delete_after=3)
            if "@" in text: text = text.replace("@", "a")
            await channel.send(text)
            print(text)
        else: await ctx.respond("You don't own the ArchiTect premium version!", ephemeral=True, delete_after=5)

    # Error handling
    @say.error
    async def say_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to send messages in the specified channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = f"An unknown error occurred. {error}"

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Say(bot))
