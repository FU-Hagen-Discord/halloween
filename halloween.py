import os

from discord import Intents, Game
from discord.ext import commands
from dotenv import load_dotenv
from typing import List

from view_manager import ViewManager

# .env file is necessary in the same directory, that contains several strings.
load_dotenv()


class HalloweenBot(commands.Bot):
    def __init__(self, *args, initial_extensions: List[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.is_prod = os.getenv("DISCORD_PROD") == "True"
        self.initial_extensions: List[str] = initial_extensions
        self.view_manager: ViewManager = ViewManager(self)
        self.persistent_views_added: bool = False

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(f"extensions.{extension}")
        await self.tree.sync()

    async def on_ready(self):
        self.view_manager.on_ready()


extensions = ["elm_street"]
bot = HalloweenBot(command_prefix='!', help_command=None, activity=Game(os.getenv('DISCORD_ACTIVITY')),
                   intents=Intents.all(), initial_extensions=extensions)
bot.run(os.getenv('DISCORD_TOKEN'))
