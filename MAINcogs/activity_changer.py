import asyncio
import random

import discord
from discord.ext import commands


class ActivityChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.change_activity_continously())
        self.time_changing_cycle = 600
        self.bot.possible_activities = {
            "Playing": [
                "Minecraft",
                "Counter Strike",
                "Among Us",
                "Rocket League",
                "Overwatch"
            ],
            "Streaming": [
                "a coding session",
                "a gaming tournament",
                "a live podcast",
                "a music concert",
                "a Q&A session"
            ],
            "Listening to": [
                "lofi beats",
                "a coding playlist",
                "a podcast",
                "an audiobook",
                "jazz music",
                "a motivational speech",
                "nature sounds"
            ],
            "Watching": [
                "a movie",
                "a live stream",
                "a tutorial",
                "a TV series",
                "a documentary",
                "a sports event",
                "an animation",
                "a comedy show"
            ],
            "Competing in": [
                "a coding challenge",
                "a gaming competition",
                "a hackathon",
                "a trivia quiz",
                "a sports tournament",
                "a talent show",
                "a debate contest",
                "a chess match"
            ]
        }

        self.activity_types: [discord.Status] = [
            discord.Status.dnd,
            discord.Status.online,
            discord.Status.idle
        ]

    async def change_activity_continously(self):
        await self.bot.wait_until_ready()
        while True:
            self.time_changing_cycle: int = random.randint(a=300, b=7200)
            activity_type, activities = random.choice(list(self.bot.possible_activities.items()))
            activity_name = random.choice(activities)
            activity_status = random.choice(self.activity_types)

            print(
                self.time_changing_cycle,
                activity_type,
                activity_name
            )

            if activity_type == "Playing":
                activity = discord.Game(name=activity_name)
            elif activity_type == "Streaming":
                activity = discord.Streaming(name=activity_name, url="http://twitch.tv/yourchannel")  # Example URL
            elif activity_type == "Listening to":
                activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
            elif activity_type == "Watching":
                activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
            elif activity_type == "Competing in":
                activity = discord.Activity(type=discord.ActivityType.competing, name=activity_name)
            else:
                activity = None

            await self.bot.change_presence(status=activity_status, activity=activity)

            await asyncio.sleep(self.time_changing_cycle)
            self.counter += 1
            print(self.counter)


def setup(bot):
    bot.add_cog(ActivityChanger(bot))
