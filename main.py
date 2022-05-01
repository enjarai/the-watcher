import datetime
import logging
import os
import sys
from abc import ABC

import nextcord
import yaml
from nextcord.ext import commands

with open('config.yml', 'r') as f:
    CONFIG = yaml.load(f, yaml.Loader)

logging.basicConfig(level=logging.INFO)
intents = nextcord.Intents.default()

cogs = [
    'litematics',
    # 'quantum_channel',
]
slash_guilds = [
    924620686486560778,
    783713805276151829
]


class Bot(commands.Bot, ABC):
    def __init__(self, config):
        self.CONFIG = config
        self.LOGGER = logging.getLogger('main')

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
                # for guild_id in slash_guilds:
                #     guild = self.get_guild(guild_id)
                #     await guild.rollout_application_commands()
                self.LOGGER.info(f'Loaded {cog}')
            await self.rollout_application_commands()
        except Exception as e:
            self.LOGGER.error(f"Could not load cog {e}")

        self.LOGGER.info("---------------The Watcher------------------"
                         f"\nBot is online and connected to {self.user}"
                         "\nCreated by enjarai"
                         f"\nConnected to {(len(self.guilds))} Guilds."
                         f"\nDetected Operating System: {sys.platform.title()}"
                         "\n--------------------------------------------")


Bot(CONFIG).run(CONFIG['token'])
