
from discord.ext import commands
import discord
from discord.commands import slash_command

from database._databaseManager import *

import json
import asyncio
import psutil
import matplotlib.pyplot as plt
from io import BytesIO


class PerformanceListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.x = []
        self.y_cpu = []
        self.y_ram = []

        self.data_window = 100
        self.bot.loop.create_task(self.check_performance_continuously())

        with open('config/globalSettings.json') as file:
            data = json.load(file)
            self.embedColor = data["globalSetting"]["embedColor"]

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]
            self.log_DB = Log(Database(logDB))

    async def check_performance_continuously(self):
        counter = 1
        while True:
            await asyncio.sleep(60)
            cpu_usage = psutil.cpu_percent(interval=0.1)
            self.y_cpu.append(cpu_usage)
            self.x.append(counter)

            ram_info = psutil.virtual_memory()
            ram_usage = ram_info.percent
            self.y_ram.append(ram_usage)

            counter += 1

            self.x = self.x[-self.data_window:]
            self.y_cpu = self.y_cpu[-self.data_window:]
            self.y_ram = self.y_ram[-self.data_window:]


    @slash_command()
    async def plot_cpu_command(self, ctx):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)
        self.plot_graph_cpu(self.x, self.y_cpu)
        filePath = 'assets/temp/cpu_performance_plot.png'
        plt.savefig(filePath)

        with open(filePath, 'rb') as f:
            file = discord.File(BytesIO(f.read()), filename='cpu_performance_plot.png')

        embed = discord.Embed(title='CPU Performance Over Time', color=int(self.embedColor, 16))
        embed.set_image(url='attachment://cpu_performance_plot.png')
        await ctx.respond(embed=embed, file=file)

    @slash_command()
    async def plot_ram_command(self, ctx):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)
        self.plot_graph_ram(self.x, self.y_ram)
        filePath = 'assets/temp/ram_performance_plot.png'
        plt.savefig(filePath)

        with open(filePath, 'rb') as f:
            file = discord.File(BytesIO(f.read()), filename='ram_performance_plot.png')

        embed = discord.Embed(title='RAM Performance Over Time', color=int(self.embedColor, 16))
        embed.set_image(url='attachment://ram_performance_plot.png')
        await ctx.respond(embed=embed, file=file)

    def plot_graph_ram(self, x: 0, y: 0):
        plt.clf()
        plt.axhspan(80, 100, facecolor='darkred', alpha=0.3)
        plt.axhspan(70, 80, facecolor='yellow', alpha=0.3)
        plt.axhspan(0, 70, facecolor='green', alpha=0.3)
        plt.plot(x, y, label='RAM Usage')
        plt.xlabel('On run time in minutes')
        plt.ylabel('RAM Usage in %')
        plt.title('RAM Usage Over Time')
        plt.legend()

    def plot_graph_cpu(self, x: 0, y: 0):
        plt.clf()
        plt.axhspan(80, 100, facecolor='darkred', alpha=0.3)
        plt.axhspan(70, 80, facecolor='yellow', alpha=0.3)
        plt.axhspan(0, 70, facecolor='green', alpha=0.3)
        plt.plot(x, y, label='CPU Usage')
        plt.xlabel('On run time in minutes')
        plt.ylabel('CPU Usage in %')
        plt.title('CPU Usage Over Time')
        plt.legend()


def setup(bot):
    bot.add_cog(PerformanceListener(bot))
