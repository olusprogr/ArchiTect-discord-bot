import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class UsersEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]
            levelDB = data["databases"]["userLevelingSystem"]

        self.economy_DB = Economy(Database(levelDB))
        self.log_DB = Log(Database(logDB))

    @slash_command(description="Claim your daily free credits!")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily_credits(self, ctx):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)
        claimedDailayCredits = self.economy_DB.insertValueIntoCredits("users", str(ctx.author.id))

        if registerOperation and claimedDailayCredits:
            embed = discord.Embed(title=f"Successfully added {claimedDailayCredits[0]} more credit(s) to your wallet!",
                                  description=f"Wallet: **{claimedDailayCredits[1]}** credits", color=0xC87A80)
            await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    @daily_credits.error
    async def daily_taskerror(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            if error.retry_after < 60:
                output = str(round(error.retry_after)) + " seconds"
            else:
                min = round(error.retry_after / 60)
                if min >= 60:
                    output = str(round(min / 60)) + " hours"
                else:
                    output = str(min) + " mintues"

            embed.description = f"You need to wait {output} before you can use this command again."

        elif isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred while executing the command: {error.original}"

        else:
            embed.description = "An unknown error occurred."
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

def setup(bot):
    bot.add_cog(UsersEconomy(bot))
