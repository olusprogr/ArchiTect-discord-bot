import asyncio
import sys
import psutil
import json

import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *


with open('config/databases.json', 'r') as file:
    data = json.load(file)

logDB = data["databases"]["savingUserOperations"]
userDB = data["databases"]["preferredUser"]


class MyView(discord.ui.View):
    def __init__(self, ctx, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = 1167786310682034246
        self.ctx = ctx
        self.bot = bot

        self.admin_DB = Administrator(Database(userDB))
        self.log_DB = Administrator(Database(logDB))

    def check_while_in(self, user_id):
        asw = self.admin_DB.checkForAdmin(user_id, "user")
        if asw:
            return True
        else:
            return False

    def return_error_msg(self):
        error_msg = "Access denied!"
        return error_msg

    def get_asw_from_db(self, interaction):
        return self.check_while_in(interaction.user.id)

    @discord.ui.button(label="Get servers", style=discord.ButtonStyle.gray, row=0)
    async def _1_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            out = ""
            for guild in self.bot.guilds:
                out += f"{guild.name}, "
            await interaction.response.send_message(f"The bot is on {len(self.bot.guilds)} servers: {out}",
                                                    delete_after=10,
                                                    ephemeral=True)
        else:
            await self.ctx.respond(self.return_error_msg(), delete_after=5, ephemeral=True)

    @discord.ui.button(label="Get logs", style=discord.ButtonStyle.gray, row=0)
    async def _2_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            output = ""
            counter = 0
            data = self.log_DB.get("log", True)

            for element in data: counter += 1
            counter -= 40

            for i in data[-40:]:
                output += f"**{str(counter)}**" + ".    " + str(f"{i}") + "\n\n"
                counter += 1

                if len(output) > 4000:
                    break

            text_without_parentheses = (output.replace('(', '')
                                              .replace(')', '')
                                              .replace("'", '')
                                              .replace(",", " |"))

            target_channel = self.bot.get_channel(self.target_channel_id)
            if target_channel:
                embed = discord.Embed(color=0xC87A80, title="Output: Log", description=text_without_parentheses)
                embed.set_footer(text=f"Executed by {self.ctx.author}")
                await target_channel.send(embed=embed)

            await self.ctx.respond("Successfully executed!", delete_after=5, ephemeral=True)

        else:
            await self.ctx.respond(self.return_error_msg(), delete_after=5, ephemeral=True)

    @discord.ui.button(label="Get preferring user", style=discord.ButtonStyle.gray, row=0)
    async def _3_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            out = self.admin_DB.get("user", True)
            original_out = ""
            for i in out:
                original_out += f"{i}\n"
            await self.ctx.respond(original_out)
        else:
            await self.ctx.respond(self.return_error_msg(), delete_after=5, ephemeral=True)

    @discord.ui.button(label="Clear logs", style=discord.ButtonStyle.red, row=1)
    async def _4_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            try:
                self.log_DB.clear_log("log")
                await self.ctx.respond("Successfully cleared the log!", delete_after=5, ephemeral=True)
            except:
                await self.ctx.respond(
                    "I couldn't clear the log. Either it has no entries or there went something wrong.",
                    delete_after=5, ephemeral=True)
        else:
            await self.ctx.respond(self.return_error_msg(), delete_after=5, ephemeral=True)

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.red, row=1)
    async def _5_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            await self.ctx.respond(content=f"{self.ctx.bot.user} is shutting down in 10sek...", delete_after=10,
                                   ephemeral=True)
            await asyncio.sleep(10)
            await sys.exit(f"{self.bot.user} is shutting down...".upper())
        else:
            await self.ctx.respond(self.return_error_msg(), delete_after=5, ephemeral=True)

    @discord.ui.button(label="Debug information", style=discord.ButtonStyle.gray, row=0)
    async def _6_button_callback(self, button, interaction):
        asw = self.get_asw_from_db(interaction)
        if asw:
            cpu_usage = psutil.cpu_percent(interval=1)

            ram_info = psutil.virtual_memory()
            total_ram = round(ram_info.total / (1024 ** 3), 2)
            available_ram = round(ram_info.available / (1024 ** 3), 2)
            used_ram = round(ram_info.used / (1024 ** 3), 2)

            embed = discord.Embed(title="DEBUG INFORMATION")
            embed.add_field(name="Host server name", value="```Kekshosting```")
            embed.add_field(name="Latency", value=f"```{round(self.bot.latency, 2)}s```")
            embed.add_field(name="RAM", value=f"```Total: {total_ram}\n"
                                              f"Available: {available_ram}\n"
                                              f"Used: {used_ram}```", inline=True)
            embed.add_field(name="CPU", value=f"```Usage: {cpu_usage}%```")
            await self.ctx.respond(embed=embed, ephemeral=True)


class Admin_overlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.check = Administrator(Database(userDB))
        self.log_DB = Log(Database(logDB))

    @slash_command(description="Enter the admin control panel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def admin_panel(self, ctx):
        await ctx.defer()

        asw = self.check.checkForAdmin(ctx.author.id, "user")
        asw2 = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        if asw and asw2:
            embed = discord.Embed(title=f"Welcome {ctx.user} to the administrators bot control panel!",
                                  description="The overlay will be deleted in 40sec.", color=0xC87A80)
            await ctx.respond(embed=embed, view=MyView(ctx, self.bot), delete_after=40)
        else:
            await ctx.respond("You are not allowed to get access to the administrator overlay!", delete_after=5,
                              ephemeral=True)

    @admin_panel.error
    async def admin_panel_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You need to wait {round(error.retry_after)} seconds before you can use this command again."
            await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

        elif isinstance(error, commands.MissingPermissions):
            embed.description = "I don't have the necessary permissions to execute this command."
            await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

        else:
            raise error


def setup(bot):
    bot.add_cog(Admin_overlay(bot))
