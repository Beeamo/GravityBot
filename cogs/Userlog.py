import discord
from discord.ext import commands
from discord import ui, app_commands
from utils.database import userdatabase
import time


class userlogs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="userlog", description="update userlog")
    @app_commands.checks.has_permissions(administrator=True)
    async def userlog(self, itx: discord.Interaction):
        userdb = userdatabase()
        users = itx.guild.members
        realusers = [user.id for user in users if not user.bot]
        userdb.verifyusers(realusers)
        await itx.response.send_message("Good", ephemeral=True)

    @app_commands.command(name="userlist", description="Displays all users")
    @app_commands.checks.has_permissions(administrator=True)
    async def userlist(self, itx: discord.Interaction):
        userdb = userdatabase()
        list = userdb.getusers()
        batch_size = 75
        for i in range(0, len(list), batch_size):
            batch = list[i:i+batch_size]
            message = ""
            for user in batch:
                message += f"<@{user}>"
            await itx.channel.send(message)
            time.sleep(1)
        await itx.followup.send("Finished")

            
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        userdb = userdatabase()
        if member.bot:
            return
        userdb.adduser(member.id)

    



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(userlogs(bot))