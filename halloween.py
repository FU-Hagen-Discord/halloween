import json

from discord import Intents, Game
from discord.ext import commands
from typing import Dict

from view_manager import ViewManager


class HalloweenBot(commands.Bot):
    def __init__(self, *args, config: Dict, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.is_prod = config["is_prod"]
        self.view_manager: ViewManager = ViewManager(self)
        self.persistent_views_added: bool = False

    async def setup_hook(self) -> None:
        for extension, _ in self.config["extensions"].items():
            await self.load_extension(f"extensions.{extension}")
        await self.tree.sync()

    async def on_ready(self):
        self.view_manager.on_ready()


def load_config():
    fp = open("config.json", mode="r")
    return json.load(fp)


config = load_config()
bot = HalloweenBot(command_prefix='!', help_command=None, activity=Game(config["activity"]),
                   intents=Intents.all(), config=config)
bot.run(config["token"])
