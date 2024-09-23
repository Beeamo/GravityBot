import discord
from discord.ext import commands
from discord import ui, app_commands
from utils.database import userdatabase
import json
import os
from dotenv import load_dotenv
from utils.RateLimiter import get_rate_limiter
import time

load_dotenv

async def roleratelimitRemove(user: discord.User, role: discord.Role):
    ratelimiter = get_rate_limiter()
    retry = True
    while retry:
        retry_duration = ratelimiter.check_request()
        if retry_duration == 0:
            await user.remove_roles(role)
            retry = False
        else:
            time.sleep(retry_duration)

async def roleratelimitAdd(user: discord.User, role: discord.Role):
    ratelimiter = get_rate_limiter()
    retry = True
    while retry:
        retry_duration = ratelimiter.check_request()
        if retry_duration == 0:
            await user.add_roles(role)
            retry = False
        else:
            time.sleep(retry_duration)

class activity(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.games = self.update_games()

    def update_games(self):
        with open("game.json", "r") as file:
            data = json.load(file)
        return data

    #account for changing real activities and from game to another activity
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        guild = self.bot.get_guild(int(os.getenv("guild")))
        user = guild.get_member(after.id)
        games = self.games
        if user not in guild.members:
            return
        if not user:
            return
        if before.bot:
            return
        for activity in before.activities:
            if activity.type == discord.ActivityType.playing and after.activity:
                for game in games:
                    role = guild.get_role(games[game])
                    if role in user.roles:
                        await roleratelimitRemove(user, role)

        for activity in after.activities:
            if before.activity:
                if before.activity.type == discord.ActivityType.playing and after.activity.type == discord.ActivityType.playing:
                    for game in games:
                        role = guild.get_role(games[game])
                        if role in user.roles:
                            await roleratelimitRemove(user, role)
            games = self.games
            if activity.name.lower() in [game.lower() for game in games]:
                role = guild.get_role(games[after.activity.name])
                await roleratelimitAdd(user, role)
                return

            for game in games:
                role = guild.get_role(games[game])
                if role in user.roles:
                    await roleratelimitRemove(user, role)
            return
        if not after.activity:
            for game in games:
                role = guild.get_role(games[game])
                if role in user.roles:
                    await roleratelimitRemove(user, role)
                

    



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(activity(bot))