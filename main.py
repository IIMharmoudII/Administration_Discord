import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

# Configurer les intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

# Variables globales
BUMP_CHANNEL_NAME = "💖・bump"  # Nom exact du salon pour les bumps
BUMP_DELAY = timedelta(hours=2)  # Délai entre deux bumps (2 heures)
lock_channel_with_countdown_task = None  # Référence à la tâche en cours
BUMP_ROLE_ID = 1314722162589831198  # ID du rôle à mentionner

# === Événement : Quand un message est envoyé ===
@bot.event
async def on_message(message):
    global lock_channel_with_countdown_task
    bump_channel = discord.utils.get(message.guild.text_channels, name=BUMP_CHANNEL_NAME)

    # Vérifie si le message contient "/bump" hors du salon désigné
    if "/bump" in message.content.lower() and message.channel != bump_channel:
        await message.delete()
        if bump_channel:
            await message.channel.send(
                f"{message.author.mention}, veuillez utiliser la commande `/bump` uniquement dans {bump_channel.mention} !",
                delete_after=5
            )
        return

    # Détecter le message de confirmation du bot Disboard
    if message.author.bot and message.author.id == 302050872383242240 and "Bump effectué !" in message.content:
        # Démarrer le verrouillage avec chrono
        await start_lockdown(bump_channel)
        return

    await bot.process_commands(message)

# === Verrouiller le salon avec un chrono ===
async def start_lockdown(channel):
    global lock_channel_with_countdown_task

    if lock_channel_with_countdown_task:
        lock_channel_with_countdown_task.cancel()

    overwrite = channel.overwrites_for(channel.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)

    lock_channel_with_countdown_task = bot.loop.create_task(lock_channel_with_countdown(channel))

async def lock_channel_with_countdown(channel):
    end_time = datetime.utcnow() + BUMP_DELAY

    while datetime.utcnow() < end_time:
        remaining_time = end_time - datetime.utcnow()
        hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await channel.edit(topic=f"⏳ Prochain bump possible dans {hours:02}:{minutes:02}:{seconds:02} !")
        await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=1))

    # Déverrouiller le salon
    overwrite = channel.overwrites_for(channel.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
    await channel.edit(topic="✅ Le serveur peut être bump à nouveau !")
    await channel.send(f"<@&{BUMP_ROLE_ID}> 🎉 C'est le moment de bump le serveur !")

# Lancer le bot
bot.run(TOKEN)
