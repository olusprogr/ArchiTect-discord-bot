import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(name="roles", description="List every role on the server")
    async def list_roles(self, ctx):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        server_id = ctx.guild.id
        server = self.bot.get_guild(server_id)
        counter = 0
        list = []

        if server is not None and registerOperation:
            roles = sorted(server.roles, key=lambda role: role.position, reverse=True)
            for role in roles:
                counter += 1
                if counter % 5 == 0:
                    list.append(f"{counter}. {role}\n")
                else:
                    list.append(f"{counter}. {role}")

            embed = discord.Embed(title="🔐ROLES/INFORMATION🔐", description="\n".join(list), color=0xC87A80)
            await ctx.respond(embed=embed)

    @list_roles.error
    async def list_roles_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.MissingPermissions):
            embed.description = "You don't have the necessary permissions to use this command."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Roles(bot))