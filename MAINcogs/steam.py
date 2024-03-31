import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from steam import Steam

from database._databaseManager import *
import json


class Steamcommands:
    def __init__(self):
        with open('config/apis/steam.json', 'r') as file: api_key = json.load(file)["steamAPI"]["key"]
        self.steam = Steam(api_key)

    def userDetails(self, userid: int or str) -> dict:
        return self.steam.users.get_user_details(userid)

    def userFriendList(self, userid: int or str) -> dict:
        return self.steam.users.get_user_friends_list(userid)

    def searchUser(self, username: str) -> dict or bool:
        user_response = self.steam.users.search_user(username)
        print(user_response)
        if user_response and "players" in user_response and len(user_response["players"]) > 0:
            return user_response
        else: return False


class Steamcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delay = 0
        self.steam = Steamcommands()

        with open('config/databases.json', 'r') as file: data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]
        userDB = data["databases"]["preferredUser"]

        self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    steam = SlashCommandGroup(name="steam", description="Steam group")

    @steam.command(description="")
    @discord.default_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def search_for_user(self, ctx, username: str):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), username)

        info = self.steam.searchUser(username)["player"]

        if info:
            embed = discord.Embed()

            embed.set_thumbnail(url=info.get('avatarfull', discord.Embed.Empty))
            embed.add_field(name="Steam ID", value=info.get('steamid', 'Not Provided'), inline=False)
            embed.add_field(name="Username", value=info.get('personaname', 'Not Provided'), inline=False)
            embed.add_field(name="Real Name", value=info.get('realname', 'Not Provided'), inline=False)
            embed.add_field(name="Profile URL", value=f"[Link]({info.get('profileurl', 'Not Provided')})", inline=False)
            embed.add_field(name="Country", value=info.get('loccountrycode', 'Not Provided'), inline=True)
            embed.add_field(name="Community Visibility", value=info.get('communityvisibilitystate', 'Not Provided'),
                            inline=True)

            await ctx.respond(embed=embed)

        else: print("user not found")

    @steam.command(description="")
    @discord.default_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def get_user_details(self, ctx, userid: str):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), userid)

        info = self.steam.userDetails(userid=userid)["player"]

        embed = discord.Embed(title="Steam User Details", color=0x00FF00)
        embed.set_thumbnail(url=info.get('avatarfull', discord.Embed.Empty))
        embed.add_field(name="Steam ID", value=info.get('steamid', 'Not Provided'), inline=False)
        embed.add_field(name="Username", value=info.get('personaname', 'Not Provided'), inline=False)
        embed.add_field(name="Real Name", value=info.get('realname', 'Not Provided'), inline=False)
        embed.add_field(name="Profile URL", value=f"[Link]({info.get('profileurl', 'Not Provided')})", inline=False)
        embed.add_field(name="Country", value=info.get('loccountrycode', 'Not Provided'), inline=True)
        embed.add_field(name="Community Visibility", value=info.get('communityvisibilitystate', 'Not Provided'),
                        inline=True)

        await ctx.respond(embed=embed)

    @steam.command(description="")
    @discord.default_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def get_user_friend_list(self, ctx, userid: str or int):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), userid)

        info = self.steam.userFriendList(userid=userid)["friends"]
        embed = discord.Embed()

        counter = 0
        for friend in info:
            if counter == 20: embed.add_field(name="Maximum friend value displayed", value="Found Friend: 20+")

            friend_name = friend.get('personaname', 'Not Provided')
            profile_url = f"[Profile URL]({friend.get('profileurl', 'Not Provided')})"
            relationship = friend.get('relationship', 'Not Provided')
            embed.add_field(name=friend_name, value=f"Relationship: {relationship}\n{profile_url}")

            counter += 1

        await ctx.respond(embed=embed)

    @steam.error
    async def steam_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error:")

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
    bot.add_cog(Steamcommand(bot))
