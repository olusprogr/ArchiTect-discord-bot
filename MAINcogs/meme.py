import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from database._databaseManager import *

import asyncpraw
import random
import json


class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]
        self.log_DB = Log(Database(logDB))

        with open('config/apis/reditt.json', 'r') as file:
            data = json.load(file)
            data = data["redittAPI"]

            self.client_id = data["clientId"]
            self.client_secret = data["clientSecret"]
            self.username = data["username"]
            self.password = data["password"]

    @slash_command(description="Get a funny trending meme")
    async def meme(self, ctx, topic: Option(str, choices=["ProgrammerHumor", "memes", "Memes_Of_The_Dank", "AnimalMemes"],
                                            description="Available channels to select: ")):

        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), topic)

        await ctx.defer()
        async with asyncpraw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=""
        ) as reddit:
            subreddit = await reddit.subreddit(topic)
            hot = subreddit.hot(limit=10)

            all_posts = []
            async for post in hot:
                await post.load()
                if post.url and not post.is_video:
                    all_posts.append(post)

            random_post = random.choice(all_posts)

            embed = discord.Embed(title=random_post.title, color=discord.Color.blurple())
            embed.set_image(url=random_post.url)

            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Meme(bot))