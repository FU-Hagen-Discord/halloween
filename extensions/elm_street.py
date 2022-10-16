import json
import os
from asyncio import sleep
from copy import deepcopy
from random import SystemRandom
from typing import Union

import discord
from discord import app_commands, Guild, Interaction, ButtonStyle
from discord.app_commands import Choice
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils import send_dm

load_dotenv()

MAX_COURAGE = 100
MIN_COURAGE = 20
MIN_COURAGE_JOIN = 50
MIN_GROUP_COURAGE = 20
INC_COURAGE_STEP = 10


def get_player_from_embed(embed: discord.Embed):
    return embed.description.split()[0].strip("<@!>")


def calculate_sweets(event):
    sweets_min = event.get("sweets_min")
    sweets_max = event.get("sweets_max")

    if sweets_min and sweets_max:
        return SystemRandom().randint(sweets_min, sweets_max)

    return None


def calculate_courage(event):
    courage_min = event.get("courage_min")
    courage_max = event.get("courage_max")

    if courage_min and courage_max:
        return SystemRandom().randint(courage_min, courage_max)

    return None


def get_doors_visited(group):
    if doors_visited := group.get("doors_visited"):
        return doors_visited
    else:
        doors_visited = []
        group["doors_visited"] = doors_visited
        return doors_visited


@app_commands.guild_only()
class ElmStreet(commands.GroupCog, name="elm"):
    def __init__(self, bot):

        self.bot = bot
        self.groups = {}
        self.players = {}
        self.story = {}
        self.load()
        self.elm_street_channel_id = int(os.getenv("DISCORD_ELM_STREET_CHANNEL"))
        self.halloween_category_id = int(os.getenv("DISCORD_HALLOWEEN_CATEGORY"))
        self.bot.view_manager.register("on_join", self.on_join)
        self.bot.view_manager.register("on_joined", self.on_joined)
        self.bot.view_manager.register("on_start", self.on_start)
        self.bot.view_manager.register("on_stop", self.on_stop)
        self.bot.view_manager.register("on_story", self.on_story)
        self.bot.view_manager.register("on_leave", self.on_leave)
        self.increase_courage.start()

    def load(self):
        try:
            with open("data/groups.json", "r") as groups_file:
                self.groups = json.load(groups_file)
        except FileNotFoundError:
            self.groups = {}

        try:
            with open("data/players.json", "r") as players_file:
                self.players = json.load(players_file)
        except FileNotFoundError:
            self.players = {}

        with open("data/story.json", "r") as story_file:
            self.story = json.load(story_file)

    def save(self):
        with open("data/groups.json", "w") as groups_file:
            json.dump(self.groups, groups_file)
        with open("data/players.json", "w") as players_file:
            json.dump(self.players, players_file)

    @app_commands.command(name="leaderboard",
                          description="Zeigt das Leaderboard der Elm Street Sammlerinnen-Gemeinschaft an.")
    @app_commands.choices(show=[Choice(name='10', value=10), Choice(name='all', value=0)])
    @app_commands.guild_only()
    async def cmd_leaderboard(self, interaction: Interaction, show: int = 10):
        await interaction.response.defer(ephemeral=True)
        leaderboard = await self.get_leaderboard(interaction.guild, max_entries=show)
        await interaction.followup.send(content=leaderboard, ephemeral=True)

    @app_commands.command(name="group-stats",
                          description="Zeigt die aktuelle Gruppenstatistik an.")
    @app_commands.guild_only()
    async def cmd_group_stats(self, interaction: Interaction):
        thread_id = interaction.channel_id
        if str(thread_id) in self.groups.keys():
            embed = await self.get_group_stats_embed(interaction.channel_id)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Gruppenstatistiken können nur in Gruppenthreads ausgegeben werden."
                                                    , ephemeral=True)

    @app_commands.command(name="leave-group",
                          description="Hiermit verlässt du deine aktuelle Gruppe")
    @app_commands.guild_only()
    async def cmd_leave_group(self, interaction: Interaction):
        thread_id = interaction.channel_id
        player_id = interaction.user.id
        if group := self.groups.get(str(thread_id)):
            if player_id == group['owner']:
                await interaction.response.send_message(
                    "Du darfst deine Gruppe nicht im Stich lassen. Als Gruppenleiterin kannst du die Gruppe höchstens "
                    "auflösen, aber nicht verlassen.", ephemeral=True)
                return

            if player_id in group.get('players'):
                self.leave_group(thread_id, player_id)
                await interaction.response.send_message(f"<@{player_id}> hat die Gruppe verlassen.")
            else:
                await interaction.response.send_message(
                    "Du bist garnicht Teil dieser Gruppe.", ephemeral=True)

        else:
            await interaction.response.send_message("Dieses Kommando kann nur in einem Gruppenthread ausgeführt werden."
                                                    , ephemeral=True)

    @app_commands.command(name="stats",
                          description="Zeigt deine persönliche Statistik an.")
    @app_commands.guild_only()
    async def cmd_stats(self, interaction: Interaction):
        embed = self.get_personal_stats_embed(interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="start-group",
                          description="Erstelle eine Gruppe für einen Streifzug durch die Elm Street")
    @app_commands.guild_only()
    async def cmd_start_group(self, interaction: Interaction, name: str):
        author = interaction.user
        category = await self.bot.fetch_channel(self.halloween_category_id)
        channel = await self.bot.fetch_channel(self.elm_street_channel_id)
        channel_type = None if self.bot.is_prod else discord.ChannelType.public_thread

        player = self.get_player(author)

        if interaction.channel != channel:
            await interaction.response.send_message(
                f"Gruppen können nur in <#{self.elm_street_channel_id}> gestartet werden.",
                ephemeral=True)
            return

        if not self.can_play(player, interaction):
            return

        thread = await channel.create_thread(name=name, auto_archive_duration=1440, type=channel_type)
        voice_channel = await category.create_voice_channel(name)
        await voice_channel.set_permissions(interaction.user, view_channel=True, connect=True)

        await thread.send(
            f"Hallo {author.mention}. Der Streifzug deiner Gruppe durch die Elm-Street findet "
            f"in diesem Thread statt. Sobald deine Gruppe sich zusammen gefunden hat, kannst "
            f"du über einen Klick auf den Start Button eure Reise starten.\n\n"
            f"Für das volle Gruselerlebnis könnt ihr euch während des Abenteuers gegenseitig "
            f"Schauermärchen in eurem Voice Channel {voice_channel.mention} erzählen.",
            view=self.get_start_view())

        await interaction.response.send_message(self.get_invite_message(author),
                                                view=self.get_join_view(thread.id))

        message = await interaction.original_response()
        self.groups[str(thread.id)] = {"message": message.id, "players": [author.id],
                                       "owner": author.id,
                                       "requests": [], 'stats': {'sweets': 0, 'courage': 0, 'doors': 0},
                                       "voice_channel": voice_channel.id}
        self.save()

    async def on_join(self, button: discord.ui.Button, interaction: Interaction, value=None):
        player = self.get_player(interaction.user)

        try:
            if group := self.groups.get(str(value)):
                requests = [r['player'] for r in group.get('requests')]
                if interaction.user.id in requests:
                    await interaction.response.send_message(
                        "Für diese Gruppe hast du dich schon beworben. Warte auf eine Entscheidung des Gruppenleiters.",
                        ephemeral=True)
                    return

                if self.is_already_in_this_group(interaction.user.id, interaction.message.id):
                    await interaction.response.send_message(
                        "Du bist schon Teil dieser Gruppe! Schau doch mal in eurem "
                        "Thread vorbei.", ephemeral=True)
                    return

                if not self.can_play(player, interaction):
                    return

                thread = await self.bot.fetch_channel(value)
                msg = await self.bot.view_manager.confirm(thread, "Neuer Rekrut",
                                                          f"{interaction.user.mention} würde sich gerne der Gruppe anschließen.",
                                                          fields=[{'name': 'aktuelle Mutpunkte',
                                                                   'value': f"{player.get('courage')}"}],
                                                          custom_prefix="rekrut",
                                                          callback_key="on_joined")
                player.get('messages').append({'id': msg.id, 'channel': thread.id})
                group.get('requests').append({'player': interaction.user.id, 'id': msg.id})
                self.save()
        except Exception as e:
            await interaction.response.send_message(
                "Ein Fehler ist aufgetreten. Überprüfe bitte, ob du der richtigen Gruppe beitreten wolltest. "
                "Sollte der Fehler erneut auftreten, sende mir (Boty McBotface) bitte eine Direktnachricht.",
                ephemeral=True)

        if not interaction.response.is_done():
            await interaction.response.send_message("Dein Wunsch, der Gruppe beizutreten wurde weitergeleitet.",
                                                    ephemeral=True)

    async def on_joined(self, button: discord.ui.Button, interaction: Interaction, value=None):
        player_id = int(get_player_from_embed(interaction.message.embeds[0]))
        thread_id = interaction.channel_id
        owner_id = self.groups.get(str(thread_id)).get('owner')

        if interaction.user.id == owner_id:
            if group := self.groups.get(str(interaction.channel_id)):
                if value:
                    if not self.is_playing(player_id, interaction, send_message=False):
                        group["players"].append(player_id)

                        # Request-Nachrichten aus allen Threads und aus players löschen
                        for thread_id in self.groups:
                            requests = self.groups.get(str(thread_id)).get('requests')
                            for request in requests:
                                if request['player'] == player_id:
                                    thread = await self.bot.fetch_channel(int(thread_id))
                                    message = await thread.fetch_message(request['id'])
                                    player = await self.bot.fetch_user(player_id)
                                    voice_channel = await self.bot.fetch_channel(group["voice_channel"])
                                    await voice_channel.set_permissions(player, view_channel=True, connect=True)
                                    await message.delete()
                                    self.delete_message_from_player(player_id, request['id'])
                                    requests.remove(request)

                        await interaction.message.channel.send(
                            f"<@!{player_id}> ist jetzt Teil der Crew! Herzlich willkommen.",
                            view=self.get_leave_view())
                        self.save()
                else:
                    await self.deny_join_request(group, interaction.message, player_id)
        else:
            await interaction.response.send_message("Nur die Gruppenerstellerin kann User annehmen oder ablehnen.",
                                                    ephemeral=True)

    async def on_start(self, button: discord.ui.Button, interaction: Interaction, value=None):
        thread_id = interaction.channel.id
        owner_id = self.groups.get(str(thread_id)).get('owner')
        if interaction.user.id == owner_id:
            if group := self.groups.get(str(interaction.channel.id)):

                elm_street_channel = await self.bot.fetch_channel(self.elm_street_channel_id)
                group_message = await elm_street_channel.fetch_message(group["message"])
                await group_message.delete()
                await interaction.response.edit_message(view=self.get_start_view(disabled=True))

                if value:  # auf Start geklickt
                    await self.deny_open_join_requests(thread_id, group)
                    random_player = await self.bot.fetch_user(SystemRandom().choice(group.get('players')))
                    bags = self.story["bags"]
                    await interaction.followup.send(
                        f"```\nSeid ihr bereit? Taschenlampe am Gürtel, Schminke im Gesicht? Dann kann es losgehen!\n"
                        f"Doch als ihr gerade in euer Abenteuer starten wollt, fällt {random_player.name} auf, "
                        f"dass ihr euch erst noch Behälter für die erwarteten Süßigkeiten suchen müsst. \n"
                        f"Ihr schnappt euch also {SystemRandom().choice(bags)} gerade da ist. \nNun aber los!\n```")
                    await self.on_story(button, interaction, "doors")
                else:  # auf Abbrechen geklickt
                    await self.end_adventure(interaction, thread_id, abort=True)
        else:
            await interaction.response.send_message(
                "Nur die Gruppenerstellerin kann die Gruppe starten lassen oder die Tour abbrechen.",
                ephemeral=True)

    async def on_stop(self, button: discord.ui.Button, interaction: Interaction, value=None):
        thread_id = interaction.channel.id

        # Button disablen
        await interaction.response.edit_message(view=self.get_stop_view(disabled=True))

        # Gruppenstatistik in elm-street posten
        stats_embed = await self.get_group_stats_embed(thread_id)
        elm_street = await self.bot.fetch_channel(self.elm_street_channel_id)
        await elm_street.send("", embed=stats_embed)

        # jedem Spieler seine Süßigkeiten geben
        sweets = self.groups.get(str(thread_id)).get('stats').get('sweets')
        self.share_sweets(sweets, thread_id)

        # aktuelles leaderboard in elm-street posten
        leaderboard = await self.get_leaderboard(interaction.guild, max_entries=0)
        await elm_street.send(leaderboard)

        await self.end_adventure(interaction, thread_id)

    async def on_story(self, button: discord.ui.Button, interaction: Interaction, value=None):
        thread_id = interaction.channel_id
        group = self.groups.get(str(thread_id))
        owner_id = group.get('owner')
        if interaction.user.id == owner_id:
            if value == "stop":
                await self.on_stop(button, interaction, value)

            elif not self.can_proceed_story(interaction.channel_id):
                value = "fear"

            if events := self.story.get("events"):
                if value == "knock_on_door":
                    group = self.groups.get(str(thread_id))
                    group_stats = group.get('stats')
                    group_stats['doors'] += 1
                    self.save()

                if event := events.get(value):
                    channel = interaction.message.channel
                    choice = self.get_choice(value, event, group)
                    if not choice:
                        view = self.get_story_view("fear")
                        await channel.send("```\nAls ihr euch auf den Weg zur nächsten Tür macht, seht ihr am Horizont "
                                           "langsam die Sonne aufgehen. Ihr betrachtet eure Beute und beschließt, "
                                           "für dieses Jahr die Jagd zu beenden und tretet den Heimweg an.\n```",
                                           view=view)
                        await interaction.message.delete()
                    else:
                        text = choice["text"]
                        view = self.get_story_view(choice.get("view"))
                        sweets = calculate_sweets(choice)
                        courage = calculate_courage(choice)
                        text = self.apply_sweets_and_courage(text, sweets, courage, interaction.channel_id)
                        await channel.send(f"```\n{text}\n```")
                        if view:
                            await channel.send("Was wollt ihr als nächstes tun?", view=view)
                        if next := choice.get("next"):
                            await self.on_story(button, interaction, next)
                        else:
                            await interaction.message.delete()
        else:
            await interaction.response.send_message("Nur die Gruppenleiterin kann die Gruppe steuern.",
                                                    ephemeral=True)

    async def on_leave(self, button: discord.ui.Button, interaction: Interaction, value=None):
        thread_id = interaction.channel_id
        player_id = interaction.user.id
        msg_player = interaction.message.mentions[0]

        if msg_player.id == player_id:
            self.leave_group(thread_id, player_id)
            await interaction.response.send_message(f"<@{player_id}> hat die Gruppe verlassen.")
            await interaction.message.edit(view=self.get_leave_view(disabled=True))
        else:
            await interaction.response.send_message(
                f"Nur <@{player_id}> darf diesen Button bedienen. Wenn du die Gruppe "
                f"verlassen willst, versuche es mit `/leave-group`", ephemeral=True)

    async def end_adventure(self, interaction: Interaction, thread_id: int, abort: bool = False):
        # voice channel löschen
        voice_channel_id = self.groups[str(thread_id)]["voice_channel"]
        voice_channel = await self.bot.fetch_channel(voice_channel_id)
        if len(voice_channel.members) == 0:
            await voice_channel.delete()

        self.groups.pop(str(thread_id))
        self.save()

        if abort:
            await interaction.followup.send(f"Du hast die Runde abgebrochen. Dieser Thread wurde "
                                            f"archiviert und du kannst in <#{self.elm_street_channel_id}>"
                                            f" eine neue Runde starten.", ephemeral=True)

        await interaction.channel.send(f"Dieses Abenteuer ist beendet und zum Nachlesen archiviert."
                                       f"\nFür mehr Halloween-Spaß, schau in <#{self.elm_street_channel_id}>"
                                       f"vorbei")
        await interaction.channel.edit(archived=True)

    def get_choice(self, key, event, group):
        if key == "doors":
            doors_visited = get_doors_visited(group)
            r = list(range(0, len(event) - 1))
            for door_visited in doors_visited:
                r.remove(door_visited)

            if len(r) == 0:
                return None

            i = SystemRandom().choice(r)
            doors_visited.append(i)
            self.save()
            return event[i]
        else:
            return SystemRandom().choice(event)

    def get_story_view(self, view_name: str):
        if views := self.story.get("views"):
            if buttons := views.get(view_name):
                return self.bot.view_manager.view(deepcopy(buttons), "on_story")

        return None

    def get_join_view(self, group_id: int):
        buttons = [
            {"label": "Join", "style": ButtonStyle.green, "value": group_id, "custom_id": "elm_street:join"}
        ]
        return self.bot.view_manager.view(buttons, "on_join")

    def get_start_view(self, disabled=False):
        buttons = [
            {"label": "Los geht's", "style": ButtonStyle.green, "value": True, "custom_id": "elm_street:start",
             "disabled": disabled},
            {"label": "Abbrechen", "style": ButtonStyle.gray, "value": False, "custom_id": "elm_street:cancel",
             "disabled": disabled}
        ]
        return self.bot.view_manager.view(buttons, "on_start")

    def get_stop_view(self, disabled=False):
        buttons = [
            {"label": "Beendet", "style": ButtonStyle.red, "custom_id": "elm_street:stop", "disabled": disabled}
        ]
        return self.bot.view_manager.view(buttons, "on_stop")

    def get_leave_view(self, disabled=False):
        buttons = [
            {"label": "Verlassen", "style": ButtonStyle.gray, "custom_id": "elm_street:leave", "disabled": disabled}
        ]
        return self.bot.view_manager.view(buttons, "on_leave")

    def can_play(self, player, interaction):
        if self.is_playing(interaction.user.id, interaction):
            return False

        if player["courage"] < MIN_COURAGE_JOIN:
            await interaction.response.send_message(
                "Du fühlst dich derzeit noch nicht mutig genug, um aus Süßigkeitenjagd zu gehen. "
                "Warte, bis deine Mutpunkte wieder mindestens 50 betragen. "
                "Den aktuellen Stand deiner Mutpunkte kannst du über /stats prüfen.",
                ephemeral=True)
            return False

        return True

    def is_playing(self, user_id: int, interaction: Interaction, send_message: bool = True):
        players = [player for player in [group["players"] for group in self.groups.values()]]
        if user_id in players:
            if send_message:
                await interaction.response.send_message(
                    "Es tut mir leid, aber du kannst nicht an mehr als einer Jagd gleichzeitig teilnehmen. "
                    "Beende erst das bisherige Abenteuer, bevor du dich einer neuen Gruppe anschließen kannst.",
                    ephemeral=True)
            return True

        return False

    def is_already_in_this_group(self, user_id, message_id):
        for group in self.groups.values():
            if message_id == group.get('message'):
                if user_id in group.get('players'):
                    return True
        return False

    def can_proceed_story(self, thread_id):
        group = self.groups.get(str(thread_id))

        player_ids = group.get("players")
        num_players = 0
        group_courage = 0

        for player_id in player_ids:
            player = self.players.get(str(player_id))
            num_players += 1
            group_courage += player["courage"]
        average_courage = group_courage / num_players

        return MIN_GROUP_COURAGE < average_courage

    def get_player(self, user: Union[discord.User, discord.Member]):
        if player := self.players.get(str(user.id)):
            return player
        else:
            player = {"courage": MAX_COURAGE, "sweets": 0, "messages": []}
            self.players[str(user.id)] = player
            self.save()
            return player

    def delete_message_from_player(self, player_id, message_id):
        if player := self.players.get(str(player_id)):
            messages = player.get('messages')
            for msg in messages:
                if msg['id'] == message_id:
                    messages.remove(msg)
                    self.save()

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
                message += f"{str(place).rjust(4)}. | {str(value).rjust(5)} | {member.display_name}#{member.discriminator}\n"
            except:
                pass

        message += f"```"

        return message

    async def get_group_stats_embed(self, thread_id):
        thread = await self.bot.fetch_channel(thread_id)
        players = self.groups.get(str(thread_id)).get('players')
        stats = self.groups.get(str(thread_id)).get('stats')

        players_value = ', '.join([f'<@{int(player)}>' for player in players])
        doors_value = stats.get('doors')
        sweets_value = stats.get('sweets')
        courage_value = stats.get('courage')

        embed = discord.Embed(title=f'Erfolge der Gruppe "{thread.name}"')
        embed.add_field(name='Mitspieler', value=players_value, inline=False)
        embed.add_field(name="Besuchte Türen", value=doors_value)
        embed.add_field(name="Gesammelte Süßigkeiten", value=sweets_value)
        embed.add_field(name="Verlorene Mutpunkte", value=courage_value)

        return embed

    def get_personal_stats_embed(self, player_id):
        player = self.players.get(str(player_id))
        embed = discord.Embed(title="Deine persönlichen Erfolge")
        embed.add_field(name="Süßigkeiten", value=player['sweets'])
        embed.add_field(name="Mutpunkte", value=player['courage'])
        return embed

    def get_invite_message(self, author):
        return SystemRandom().choice(self.story["invitations"]).format(author_mention=author.mention)

    def get_group_by_voice_id(self, voice_id):
        for group in self.groups.values():
            if vc := group.get("voice_channel"):
                if vc == voice_id:
                    return group

        return None

    def apply_sweets_and_courage(self, text, sweets, courage, thread_id):
        group = self.groups.get(str(thread_id))
        player_ids = group.get("players")
        group_stats = group.get('stats')

        if sweets:
            if sweets > 0:
                text += f"\n\nIhr erhaltet jeweils {sweets} Süßigkeiten."
            if sweets == 0:
                text += f"\n\nIhr habt genau so viele Süßigkeiten wie vorher."
            if sweets < 0:
                text += f"\n\nIhr verliert jeweils {-sweets} Süßigkeiten."
            group_stats['sweets'] += sweets
        if courage:
            if courage > 0:
                text += f"\n\nIhr verliert jeweils {courage} Mutpunkte."
            for player_id in player_ids:
                player = self.players.get(str(player_id))
                player["courage"] -= courage
            group_stats['courage'] += courage

        self.save()
        # TODO Was passiert wenn die courage eines Players zu weit sinkt?
        return text

    def share_sweets(self, sweets, thread_id):
        group = self.groups.get(str(thread_id))
        player_ids = group.get("players")
        for player_id in player_ids:
            player = self.players.get(str(player_id))
            player["sweets"] += sweets

    def leave_group(self, thread_id, player_id):
        group = self.groups.get(str(thread_id))
        group_players = group.get('players')
        player = self.players.get(str(player_id))

        # Spieler auszahlen
        group_stats = group.get('stats')
        player["sweets"] += group_stats['sweets']

        # Spieler aus Gruppe löschen
        group_players.remove(player_id)
        self.save()

    async def deny_join_request(self, group, message, player_id):
        user = self.bot.get_user(player_id)
        outfit = ["Piraten", "Einhörner", "Geister", "Katzen", "Weihnachtswichtel"]
        dresscode = ["Werwölfe", "Vampire", "Alice im Wunderland", "Hexen", "Zombies"]
        texts = [
            "Wir wollen um die Häuser ziehen und Kinder erschrecken. Du schaust aus, als würdest du den "
            "Kindern lieber unsere Süßigkeiten geben. Versuch es woanders.",
            f"Ich glaub du hast dich verlaufen, in dieser Gruppe können wir keine "
            f"{SystemRandom().choice(outfit)} gebrauchen. Unser Dresscode ist: {SystemRandom().choice(dresscode)}."]
        await send_dm(user, SystemRandom().choice(texts))
        group["requests"].remove({'player': player_id, 'id': message.id})
        self.save()
        # Request Nachricht aus diesem Thread und aus players löschen
        self.delete_message_from_player(player_id, message.id)
        await message.delete()

    async def deny_open_join_requests(self, thread_id, group):
        thread = await self.bot.fetch_channel(thread_id)

        if requests := group.get("requests"):
            for request in requests:
                message = await thread.fetch_message(request["id"])
                await self.deny_join_request(group, message, request["player"])

    @tasks.loop(minutes=5)
    async def increase_courage(self):
        # Alle Spieler, die gerade in einer Runde sind auslesen
        actual_playing = [player for player in [group["players"] for group in self.groups.values()]]

        # pro Spieler: courage erhöhen
        for player_id, player in self.players.items():
            # nur wenn Spieler nicht gerade spielt
            if int(player_id) not in actual_playing:
                courage = player.get('courage')
                if courage < MAX_COURAGE:
                    player['courage'] = min(courage + INC_COURAGE_STEP, MAX_COURAGE)
                    self.save()

                    # pro Nachricht: Nachricht erneuern
                    if messages := player.get('messages'):
                        for message in messages:
                            channel = await self.bot.fetch_channel(message['channel'])
                            msg = await channel.fetch_message(message['id'])
                            embed = msg.embeds[0]
                            embed.clear_fields()
                            embed.add_field(name='aktuelle Mutpunkte', value=f"{player.get('courage')}")
                            await msg.edit(embed=embed)

    @increase_courage.before_loop
    async def before_increase(self):
        await sleep(10)

    @commands.Cog.listener(name="on_voice_state_update")
    async def voice_state_changed(self, member, before, after):
        if not after.channel:
            voice_channel_left = before.channel
            if len(voice_channel_left.members) == 0 and \
                    voice_channel_left.category_id == self.halloween_category_id and \
                    not self.get_group_by_voice_id(voice_channel_left.id):
                await voice_channel_left.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ElmStreet(bot))
