import json
import os
import random
from typing import Dict
from datetime import datetime, timedelta

import discord
from discord import app_commands, Guild, Interaction, ButtonStyle, Message, Embed
from discord.app_commands import Choice
from discord.ext import commands, tasks


@app_commands.guild_only()
class ClickGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config: Dict = bot.config["extensions"][__name__.split(".")[-1]]
        self.bot.view_manager.register("on_click", self.on_click)
        self.players = {}
        self.msg_count: int = 0
        self.last_sent: datetime = datetime(1970, 1, 1)
        self.load()

    def load(self):
        try:
            with open("data/players.json", "r") as players_file:
                self.players = json.load(players_file)
        except FileNotFoundError:
            pass

    def save(self):
        with open("data/players.json", "w") as players_file:
            json.dump(self.players, players_file)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.config["channels"]:
            return

        self.msg_count += 1
        if self.msg_count < self.config["min_msg_count"]:
            print("Too few messages sent.")
            return

        if self.last_sent + timedelta(minutes=self.config["cooldown"]) > datetime.now():
            print("Too early, sorry.")
            return

        if random.random() > self.config["probability"]:
            print("Nope, better luck next time!")
            return

        await self.send_message(message.channel)

    async def send_message(self, channel) -> None:
        img = self.get_random_image()
        plus_emoji, minus_emoji = self.get_random_emojis()
        file = discord.File(f"{self.config['img_dir']}/{img}", filename=img)
        embed = Embed(title=self.config["messages"]["title"],
                      description=self.get_random_description(plus_emoji, minus_emoji))
        embed.set_image(url=f"attachment://{img}")
        await channel.send(file=file, embed=embed, view=self.get_view(plus_emoji, minus_emoji))

        self.last_sent = datetime.now()
        self.msg_count = 0

    def get_random_image(self) -> str:
        images = os.listdir(self.config["img_dir"])
        return random.choice(images)

    def get_random_emojis(self):
        random.shuffle(self.config["emojis"])
        return self.config["emojis"][0], self.config["emojis"][1]

    def get_random_description(self, plus_emoji, minus_emoji):
        texts = self.config["messages"]["descriptions"]
        return random.choice(texts).format(plus_emoji=plus_emoji, minus_emoji=minus_emoji)

    @app_commands.command(name="leaderboard",
                          description="Zeigt das Leaderboard an.")
    @app_commands.choices(show=[Choice(name='10', value=10), Choice(name='all', value=0)])
    @app_commands.describe(show="Gib an, wie viele Einträge des Leaderboards du sehen möchtest.",
                           public="Gib an, ob du das Leaderboard für dich persönlich, oder für alle anzeigen lassen möchtest.")
    @app_commands.guild_only()
    async def cmd_leaderboard(self, interaction: Interaction, show: int = 10, public: bool = False):
        await interaction.response.defer(ephemeral=not public)
        leaderboard = await self.get_leaderboard(interaction.guild, max_entries=show)
        await interaction.followup.send(content=leaderboard, ephemeral=not public)

    async def on_click(self, button: discord.ui.Button, interaction: Interaction, value=None):
        player = self.get_player(interaction.user.id)

        if player.get(str(interaction.message.id)):
            await interaction.response.send_message(
                self.config["messages"]["duplicate"], ephemeral=True)
            return

        player[str(interaction.message.id)] = value

        if value > 0:
            await interaction.response.send_message(
                self.config["messages"]["plus"].format(value=value), ephemeral=True)
            button.value -= 1
        elif value < 0:
            await interaction.response.send_message(
                self.config["messages"]["minus"].format(value=-value),
                ephemeral=True)
            button.value += 1
        else:
            interaction.response.send_message(self.config["messages"]["too_late"], ephemeral=True)

        self.save()

        if button.value == 0 and interaction.message:
            await interaction.message.delete()

    def get_view(self, plus_emoji, minus_emoji):
        buttons = [
            {"style": ButtonStyle.gray, "value": self.config["max_points"], "custom_id": "click_game:plus",
             "emoji": plus_emoji},
            {"style": ButtonStyle.gray, "value": -1 * self.config["max_points"], "custom_id": "click_game:minus",
             "emoji": minus_emoji}
        ]

        random.shuffle(buttons)

        return self.bot.view_manager.view(buttons, "on_click")

    def get_player(self, user_id: int):
        if player := self.players.get(str(user_id)):
            return player

        player = {}
        self.players[str(user_id)] = player
        return player

    async def get_leaderboard(self, guild: Guild, max_entries: int = 10):
        message = f"**__Leaderboard__**\n\n" \
                  f"{self.config['leaderboard_emoji'] * 8}\n\n" \
                  f"```md\n" \
                  f"Rank. | Items | User\n" \
                  f"==================================================\n"

        place = 0
        scores = self.get_scores()
        ready = False
        last_score = -1
        for player_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
            member = await guild.fetch_member(int(player_id))
            try:
                if last_score != score:
                    place += 1
                last_score = score
                if 0 < max_entries < place:
                    if ready:
                        break
                message += f"{str(place).rjust(4)}. | {str(score).rjust(5)} | "
                message += f"@{member.name}"
                message += f"#{member.discriminator}\n" if member.discriminator != "0" else "\n"
            except:
                pass

        message += f"```"

        return message

    def get_scores(self):
        scores = {}
        for player_id, messages in self.players.items():
            score = 0
            for value in messages.values():
                score += value
            scores[player_id] = score

        return scores


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ClickGame(bot))
