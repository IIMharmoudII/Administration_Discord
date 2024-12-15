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
BUMP_ROLE_ID = 1314722162589831198  # ID du rôle à mentionner
DISBOARD_BOT_ID = 302050872383242240  # ID de Disboard

# === Événement : Quand un message est envoyé ===
@bot.event
async def on_message(message):
    if message.guild is None:  # Ignorer les messages privés
        return

    bump_channel = discord.utils.get(message.guild.text_channels, name=BUMP_CHANNEL_NAME)

    # Vérifie si le message provient de Disboard dans le salon de bump
    if (
        message.channel == bump_channel
        and message.author.bot
        and message.author.id == DISBOARD_BOT_ID
        and "Bump effectué !" in message.content
    ):
        await start_slowmode_and_timer(bump_channel)
        return

    await bot.process_commands(message)

# === Activer le mode lent et lancer le chrono ===
async def start_slowmode_and_timer(channel):
    # Activer le mode lent pour 2 heures
    await channel.edit(slowmode_delay=int(BUMP_DELAY.total_seconds()))

    # Mettre à jour le sujet du salon avec un chrono
    end_time = datetime.utcnow() + BUMP_DELAY

    while datetime.utcnow() < end_time:
        remaining_time = end_time - datetime.utcnow()
        hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await channel.edit(topic=f"⏳ Prochain bump possible dans {hours:02}:{minutes:02}:{seconds:02} !")
        await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=1))

    # Désactiver le mode lent et notifier les utilisateurs
    await channel.edit(slowmode_delay=0, topic="✅ Le serveur peut être bump à nouveau !")
    await channel.send(f"<@&{BUMP_ROLE_ID}> 🎉 C'est le moment de bump le serveur !")

# Lancer le bot
bot.run(TOKEN)
