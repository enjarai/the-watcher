import datetime
import os
import sys
from abc import ABC

import nextcord
import yaml
from nextcord.ext import commands

with open('config.yml', 'r') as f:
    CONFIG = yaml.load(f, yaml.Loader)

intents = nextcord.Intents.default()
intents.messages = True

cogs = [
    'litematics'
]


class Bot(commands.Bot, ABC):
    def __init__(self, config):
        self.CONFIG = config

        super().__init__(
            command_prefix="!",
            intents=intents,
            owner_id=self.CONFIG['owner_id'],
            reconnect=True,
            case_insensitive=False
        )

        if not os.path.exists(self.CONFIG['temp_directory']):
            os.mkdir(self.CONFIG['temp_directory'])

        self.uptime = None

        self.remove_command('help')
        self.loop.create_task(self.ready())

    async def ready(self):
        await self.wait_until_ready()

        # await self.change_presence(activity=discord.Activity(type=type, name=activity))

        if not self.uptime:
            self.uptime = datetime.datetime.utcnow()

        try:
            for cog in cogs:
                self.load_extension(f"cogs.{cog}")
                print(f'Loaded {cog}')
        except Exception as e:
            print(f"Could not load cog {e}")

        print("---------------The Watcher------------------"
              f"\nBot is online and connected to {self.user}"
              "\nCreated by enjarai"
              f"\nConnected to {(len(self.guilds))} Guilds."
              f"\nDetected Operating System: {sys.platform.title()}"
              "\n--------------------------------------------")


Bot(CONFIG).run(CONFIG['token'])
