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
        self.msg_count: int = 0
        self.last_sent: datetime = datetime(1970, 1, 1)

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
        file = discord.File(f"images/{img}", filename=img)
        embed = Embed(title="Vorsicht!", description=self.get_random_description(plus_emoji, minus_emoji))
        embed.set_image(url=f"attachment://{img}")
        await channel.send(file=file, embed=embed, view=self.get_view(plus_emoji, minus_emoji))

        self.last_sent = datetime.now()
        self.msg_count = 0

    def get_random_image(self) -> str:
        images = os.listdir("images/")
        return random.choice(images)

    def get_random_emojis(self):
        plus_emoji = random.choice(self.config["emojis"])
        while True:
            minus_emoji = random.choice(self.config["emojis"])
            if plus_emoji != minus_emoji:
                return plus_emoji, minus_emoji

    def get_random_description(self, plus_emoji, minus_emoji):
        texts = [
            f"Oh nein, pass auf! Klicke auf {plus_emoji}, um das Monster in die Flucht zu schlagen! Klicke auf {minus_emoji} um das Monster zu stärken!",
            f"Oh nein, pass auf! Klicke auf {minus_emoji} um das Monster zu stärken! Klicke auf {plus_emoji}, um das Monster in die Flucht zu schlagen!"]
        return random.choice(texts)

    @app_commands.command(name="leaderboard",
                          description="Zeigt das Leaderboard der Elm Street Sammlerinnen-Gemeinschaft an.")
    @app_commands.choices(show=[Choice(name='10', value=10), Choice(name='all', value=0)])
    @app_commands.guild_only()
    async def cmd_leaderboard(self, interaction: Interaction, show: int = 10):
        await interaction.response.defer(ephemeral=True)
        leaderboard = await self.get_leaderboard(interaction.guild, max_entries=show)
        await interaction.followup.send(content=leaderboard, ephemeral=True)

    async def on_click(self, button: discord.ui.Button, interaction: Interaction, value=None):
        if value > 0:
            await interaction.response.send_message(
                f"Super! Du hast das Monster geschwächt und erhältst zur Belohnung {value} Punkte.", ephemeral=True)
            button.value -= 1
        elif value < 0:
            await interaction.response.send_message(
                f"Oh nein! Du hast das Monster gestärkt. Es greift dich an und du bekommst {value} Punkte abgezogen.",
                ephemeral=True)
            button.value += 1
        else:
            interaction.response.send_message("Du warst zu spät. Glücklicherweise wurde das Monster bereits besiegt.",
                                              ephemeral=True)

        if button.value == 0 and interaction.message:
            await interaction.message.delete()

    def get_view(self, plus_emoji, minus_emoji):
        buttons = [
            {"style": ButtonStyle.gray, "value": 5, "custom_id": "click_game:plus", "emoji": plus_emoji},
            {"style": ButtonStyle.gray, "value": -5, "custom_id": "click_game:minus", "emoji": minus_emoji}
        ]

        random.shuffle(buttons)

        return self.bot.view_manager.view(buttons, "on_click")

    async def get_leaderboard(self, guild: Guild, max_entries: int = 10):
        message = f"**__Elm-Street Leaderboard__**\n\n" \
                  f"Wie süß bist du wirklich??\n" \
                  f"{':jack_o_lantern: ' * 8}\n\n" \
                  f"```md\n" \
                  f"Rank. | Items | User\n" \
                  f"==================================================\n"

        place = 0

        ready = False
        last_score = -1
        for player_id, player_data in sorted(self.players.items(), key=lambda item: item[1]["sweets"], reverse=True):
            value = player_data["sweets"]
            member = await guild.fetch_member(int(player_id))
            try:
                if last_score != value:
                    place += 1
                last_score = value
                if 0 < max_entries < place:
                    if ready:
                        break
                message += f"{str(place).rjust(4)}. | {str(value).rjust(5)} | "
                message += f"{member.display_name}#{member.discriminator}\n"
            except:
                pass

        message += f"```"

        return message

    @tasks.loop(minutes=5)
    async def increase_courage(self):
        pass

    @increase_courage.before_loop
    async def before_increase(self):
        pass
        # await sleep(10)

    # @commands.Cog.listener(name="on_voice_state_update")
    # async def voice_state_changed(self, member, before, after):
    #     if not after.channel:
    #         voice_channel_left = before.channel
    #         if len(voice_channel_left.members) == 0 and \
    #                 voice_channel_left.category_id == self.halloween_category_id and \
    #                 not self.get_group_by_voice_id(voice_channel_left.id):
    #             await voice_channel_left.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ClickGame(bot))
