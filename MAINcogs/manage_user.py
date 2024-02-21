import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext.commands import MissingPermissions

from database._databaseManager import *

import json
from datetime import timedelta


class manage_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Ban a Member")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @discord.default_permissions(ban_members=True)
    async def ban(self, ctx, member: Option(discord.Member, "Wähle einen Member"),
                  reason: Option(str, "Describe the reason for the kick. ", required=False)):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}, {reason}")

        if member.id == ctx.author.id:
            await ctx.respond("You cannot ban yourself", ephemeral=True, delete_after=5)
        elif member.guild_permissions.administrator:
            await ctx.respond("Stop trying to ban an admin! ", ephemeral=True, delete_after=5)
        else:
            if reason == None:
                reason = "None provided."
            if registerOperation: await member.ban(reason=reason)
            await ctx.respond(f"<@{member.id}> has been banned!\n", ephemeral=True, delete_after=3)

    @ban.error
    async def ban_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have ban members permissions!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "Something went wrong... Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    # ---------------------------------------------------------------------

    @slash_command(description="Kick a member ")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @discord.default_permissions(kick_members=True)
    async def kick(self, ctx, member: Option(discord.Member, "Wähle einen Member"),
                   reason: Option(str, "Desccribe the reason for the kick. ", required=False)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}, {reason}")

        if ctx.author.id == member.id:
            await ctx.respond("You cannot kick yourself", ephemeral=True, delete_after=5)
        elif member.guild_permissions.administrator:
            await ctx.respond("Stop trying to kick an admin! ", ephemeral=True, delete_after=5)
        else:
            if reason == None:
                reason = "None provided."
            await member.kick(reason=reason)
            await ctx.respond(f"<@{member.id}> has been kicked out!\n", ephemeral=True, delete_after=3)

    @kick.error
    async def kick_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have kick members permissions!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "Something went wrong... Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

    # ---------------------------------------------------------------------

    @slash_command(name='timeout', description="Mutes/timeouts a member")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: Option(discord.Member, required=True), reason: Option(str, required=False),
                      days: Option(int, max_value=27, default=0, required=False),
                      hours: Option(int, default=0, required=False), minutes: Option(int, default=0, required=False)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}, {reason}, {days}, {hours}")

        if member.id == ctx.author.id:
            await ctx.respond("You can't timeout yourself!")
            return
        if member.guild_permissions.moderate_members:
            await ctx.respond("You can't do this, this person is a moderator!")
            return
        duration = timedelta(days=days, hours=hours, minutes=minutes)
        if duration >= timedelta(days=28):
            await ctx.respond("I can't mute someone for more than 28 days!",
                              ephemeral=True)
            return
        if reason is None:
            await member.timeout_for(duration)
            await ctx.respond(
                f"<@{member.id}> has been timed out for {days} days, {hours} hours and {minutes} minutes by <@{ctx.author.id}>.", ephemeral=True, delete_after=15)
        else:
            await member.timeout_for(duration, reason=reason)
            await ctx.respond(
                f"<@{member.id}> has been timed out for {days} days, {hours} hours and {minutes} minutes by <@{ctx.author.id}> for '{reason}'.", ephemeral=True, delete_after=15)

    @timeout.error
    async def timeout_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have moderate members permissions!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            raise error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    @slash_command(name='unmute', description="Unmutes/untimeouts a member")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: Option(discord.Member, required=True), reason: Option(str, required=False)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}, {reason}")

        if reason == None:
            await member.remove_timeout()
            await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}>.", ephemeral=True, delete_after=15)
        else:
            await member.remove_timeout(reason=reason)
            await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}> for '{reason}'.", ephemeral=True, delete_after=15)

    @unmute.error
    async def unmute_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have moderate members permissions!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            raise error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    # ---------------------------------------------------------------------

    nick = SlashCommandGroup(name="nick", description="Nickname group")

    @nick.command(description="Edit the nickname of someone")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_nicknames=True)
    async def set(self, ctx, member: Option(discord.Member), nickname: Option(str)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}, {nickname}")

        if member.guild_permissions.administrator:
            await ctx.respond("We can't change the nickname of an administrator without any permissions!",
                              ephemeral=True, delete_after=10)
            return
        else:
            await member.edit(nick=nickname)
            await ctx.respond("Nickname has been changed.", ephemeral=True, delete_after=3)

    @set.error
    async def set_error(self, ctx, error):
        embed = discord.Embed(color=0x7E83AD, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have manage nicknames permission!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            raise error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

    @nick.command(description="Set the current nickname to default.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_nicknames=True)
    async def default(self, ctx, member: Option(discord.Member)):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{member}")

        if member.guild_permissions.administrator:
            await ctx.respond("We can't change the nickname of an administrator without any permissions!",
                              ephemeral=True, delete_after=10)
            return
        else:
            await member.edit(nick=None)
            await ctx.respond("Nickname has been reseted.", ephemeral=True, delete_after=3)

    @default.error
    async def default_error(self, ctx, error):
        embed = discord.Embed(color=0x7E83AD, title="Error: ")

        if isinstance(error, MissingPermissions):
            embed.description = "You can't do this! You need to have change nicknames permission!"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            raise error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(manage_user(bot))
