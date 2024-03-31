import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from database._databaseManager import *
import asyncio
import json


class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delay = 0

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]
        userDB = data["databases"]["preferredUser"]

        self.check = Administrator(Database(userDB))
        #self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    @slash_command(description="Spam a word with your personalized parameters")
    @discord.default_permissions(manage_messages=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def spam(self, ctx,
                   text: Option(str, description="Type in the text you want to spam in. "),
                   amount: Option(int, max_value=100, min_value=2, description="How often should it spam? "),
                   channel: Option(discord.TextChannel, "Select a Textchannel.", required=False)
                   ):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{text}, {amount}, {channel}")

        if "@everyone" in text:
            await ctx.respond("Pinging the whole server is strongly forbidden especially in communities server!")
            return

        elif "@here" in text:
            await ctx.respond("Pinging the whole server is strongly forbidden especially in communities server!")
            return

        else:
            asw = self.check.checkForPremium(ctx.author.id, "user")
            if asw is True:
                await ctx.respond(f"Here you go!\nCalculated runtime: +-{amount}seconds.", ephemeral=True,
                                  delete_after=3)
                if channel is None:
                    channel = ctx.channel
                    for i in range(amount):
                        await channel.send(text)
                        await asyncio.sleep(self.delay)

                else:
                    for i in range(amount):
                        await ctx.channel.send(text)
                        await asyncio.sleep(self.delay)

            else:
                await ctx.respond("You don't own the ArchiTect premium version!", ephemeral=True, delete_after=5)

    @spam.error
    async def spam_error(self, ctx, error):
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

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Spam(bot))
