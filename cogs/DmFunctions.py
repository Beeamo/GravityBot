import discord
from discord.ext import commands
from discord import ui, app_commands
import asyncio
import time
from utils.DmQueue import MessageQueue, get_dm_queue

class DMAllForm(ui.Modal, title="Message All"):
    
    def __init__(self, ticket_name, botclient):
        super(DMAllForm, self).__init__(timeout=None)
        self.ticket_name = ticket_name
        self.bot = botclient
 
    Message = ui.TextInput(
        label="Message",
        style=discord.TextStyle.long,
        placeholder="",
        max_length=1900,
        required=True)
 
    async def on_submit(self, itx: discord.Interaction):
        queue = get_dm_queue(self.bot)
        queue.add_message(self.Message.value, itx.guild.id, itx.guild.members)
        await  itx.response.send_message(f"Sending message to all members. This will take ~{itx.guild.member_count * 11} seconds.", ephemeral=True)
        return

class DMRoleForm(ui.Modal, title="Message Role"):
    
    def __init__(self, ticket_name, botclient):
        super(DMRoleForm, self).__init__(timeout=None)
        self.ticket_name = ticket_name
        self.bot = botclient
 
    Message = ui.TextInput(
        label="Message",
        style=discord.TextStyle.long,
        placeholder="",
        max_length=1900,
        required=True)
 
    async def on_submit(self, itx: discord.Interaction):
        role = itx.guild.get_role(int(self.ticket_name))
        queue = get_dm_queue(self.bot)
        queue.add_message(self.Message.value, itx.guild.id, role.members)
        await  itx.response.send_message(f"Sending message to all members with. This will take ~{len(role.members * 11)} seconds.", ephemeral=True)
        return

class DmGroup(commands.GroupCog, name="dm", description="Dm Options"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.loop.create_task(self.message_queue_worker())

    @app_commands.command(name="all", description="Dm all members of the server")
    @app_commands.checks.has_permissions(administrator=True)
    async def dmall(self, itx: discord.Interaction):
        await  itx.response.send_modal(DMAllForm("Custom Message", self.bot))

    @app_commands.command(name="role", description="Dm members of a role")
    @app_commands.checks.has_permissions(administrator=True)
    async def dmrole(self, itx: discord.Interaction, role: discord.Role):
        await  itx.response.send_modal(DMRoleForm(str(role.id), self.bot))

    @app_commands.command(name="pause", description="pause dm actions")
    @app_commands.checks.has_permissions(administrator=True)
    async def pause(self, itx: discord.Interaction):
        queue = get_dm_queue(self.bot)
        await queue.pause()
        await itx.response.send_message("Messaging has been paused", ephemeral=True)

    @app_commands.command(name="resume", description="resume dm actions")
    @app_commands.checks.has_permissions(administrator=True)
    async def resume(self, itx: discord.Interaction):
        queue = get_dm_queue(self.bot)
        await queue.resume()
        await itx.response.send_message("Messaging has been resumed", ephemeral=True)

    async def message_queue_worker(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            queue = get_dm_queue(self.bot)
            await queue.process_queue()
            await asyncio.sleep(1)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DmGroup(bot))