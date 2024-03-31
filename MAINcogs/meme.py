import asyncio

import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from database._databaseManager import *

import asyncpraw
import random
import json
import requests
from PIL import Image
from io import BytesIO


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

    @commands.cooldown(1, 60, commands.BucketType.user)
    @slash_command(description="Get a funny trending meme")
    async def meme(self, ctx, topic: Option(str, choices=["ProgrammerHumor", "memes", "Memes_Of_The_Dank", "AnimalMemes"],
                                            description="Available channels to select: ")):

        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), topic)

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

            response = requests.get(post.url)

            content_type = response.headers.get('content-type')

            if content_type.startswith('image'):
                image_bytes = BytesIO(response.content)
                image = Image.open(image_bytes)

                max_size = (100, 100)
                image.thumbnail(max_size)

                width, height = image.size
                total_red, total_green, total_blue = 0, 0, 0

                for y in range(height):
                    for x in range(width):
                        pixel = image.getpixel((x, y))
                        total_red += pixel[0]
                        total_green += pixel[1]
                        total_blue += pixel[2]

                average_red = total_red // (width * height)
                average_green = total_green // (width * height)
                average_blue = total_blue // (width * height)

                hex_color = "0x{:02x}{:02x}{:02x}".format(average_red, average_green, average_blue)

                embed = discord.Embed(title=random_post.title, color=int(hex_color, 16))
                embed.set_image(url=random_post.url)

            else:
                embed = discord.Embed(title=random_post.title, color=0xC87A80)

            if registerOperation: await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Meme(bot))
