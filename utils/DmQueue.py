import asyncio
import aiofiles
import discord
import time
import random
import uuid6
import json
import threading
class MessageQueue():
    def __init__(self, discordbot):
        self.queue = []
        self.paused = False
        self.bot = discordbot
        self.dmstorage_lock = threading.Lock()
        self.dmcurrent_lock = threading.Lock()
        self.initial_populate_queue()


    def initial_populate_queue(self):
        with self.dmcurrent_lock:
            try:
                with open('currentdm.json', 'r') as currentdm_file:
                    currentdm_data = json.load(currentdm_file)
                    for mid in currentdm_data:
                        self.queue.append(mid)
            except FileNotFoundError:
                pass

        with self.dmstorage_lock:
            try:
                with open('dmstorage.json', 'r') as dmstorage_file:
                    dmstorage_data = json.load(dmstorage_file)
                    for mid in dmstorage_data:
                        self.queue.append(mid)
            except FileNotFoundError:
                pass
    
    async def send_message(self, mid, delay=35):
        with self.dmcurrent_lock:
            async with aiofiles.open('currentdm.json', 'r') as dmstorager:
                queuehandler = json.loads(await dmstorager.read())
        if not queuehandler or (isinstance(queuehandler, dict) and not queuehandler):
            with self.dmstorage_lock:
                async with aiofiles.open('dmstorage.json', 'r') as dmstorager:
                    queuehandler = json.loads(await dmstorager.read())
            with self.dmcurrent_lock:
                temp = {}
                temp[mid] = queuehandler
                queuehandler = temp
                async with aiofiles.open('currentdm.json', 'w') as dmstoragew:
                    await dmstoragew.write(json.dumps(queuehandler[mid], indent=4))
            temp = queuehandler
            del temp[mid]
            with self.dmstorage_lock:
                async with aiofiles.open('dmstorage.json', 'w') as dmstoragew:
                    await dmstoragew.write(json.dumps(temp, indent=4))
            with self.dmcurrent_lock:
                async with aiofiles.open('currentdm.json', 'r') as dmstorager:
                    queuehandler = json.loads(await dmstorager.read())
     

        guild = self.bot.get_guild(queuehandler[mid]["server"])
        userlist = queuehandler[mid]["members"]

        # Create a separate list for non-bot members
        non_bot_members = [member_id for member_id in userlist if not guild.get_member(member_id).bot]

        # Create a copy of the userlist
        userlist_copy = list(non_bot_members)
        for memberid in non_bot_members:
            member = guild.get_member(memberid)
            spaces = random.randint(1, 4) * "​"
            try:
                while self.paused:
                    await asyncio.sleep(1)
                
                await member.send(queuehandler[mid]["message"] + spaces)
                await asyncio.sleep(delay)
                userlist_copy.remove(memberid)
                
            except Exception as e:
                print(f"Issue messaging {member} in dm all: {e}")
                userlist_copy.remove(memberid)
                
            queuehandler[mid]["members"] = userlist_copy
                
            # Writing changes back to the file
            with self.dmcurrent_lock:
                async with aiofiles.open('currentdm.json', 'w') as dmstoragew:
                    await dmstoragew.write(json.dumps(queuehandler, indent=4))   
        clean = {}
        with self.dmcurrent_lock:
            async with aiofiles.open('currentdm.json', 'w') as dmstoragew:
                await dmstoragew.write(json.dumps(clean, indent=4))

    def add_message(self, message, serverid, members):
        mid = uuid6.uuid7()
        mid = mid.int
        with self.dmstorage_lock:
            with open('dmstorage.json', 'r') as dmstorager:
                value = json.load(dmstorager)
        value[mid] = {}
        value[mid]["message"] = message
        value[mid]["server"] = serverid
        memberidlist = [member.id for member in members]
        value[mid]["members"] = memberidlist
        with self.dmstorage_lock:
            with open('dmstorage.json', 'w') as dmstorage:
                json.dump(value, dmstorage, indent=4)
        self.queue.append(mid)

    async def process_queue(self):
        while self.queue:
            mid = self.queue.pop(0)
            await self.send_message(str(mid))

    async def pause(self):
        self.paused = True

    async def resume(self):
        self.paused = False

dm_queue_instance = None

def get_dm_queue(bot):
    global dm_queue_instance
    if dm_queue_instance is None:
        dm_queue_instance = MessageQueue(bot)
    return dm_queue_instance
