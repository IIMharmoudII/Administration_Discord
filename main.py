import discord
from discord.ext import commands
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

# === Événement : Quand le bot est prêt ===
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    for guild in bot.guilds:
        bump_channel = discord.utils.get(guild.text_channels, name=BUMP_CHANNEL_NAME)
        if bump_channel:
            await check_previous_bump(bump_channel)

# === Vérification de l'historique des messages ===
async def check_previous_bump(channel):
    async for message in channel.history(limit=50):  # Parcourir les 50 derniers messages
        if (
            message.author.bot
            and message.author.id == DISBOARD_BOT_ID
            and "Bump effectué !" in message.content
        ):
            last_bump_time = message.created_at
            now = datetime.utcnow()
            time_elapsed = now - last_bump_time
            time_remaining = max(BUMP_DELAY - time_elapsed, timedelta(0))

            if time_remaining > timedelta(0):
                # Activer le mode lent et démarrer le chrono si nécessaire
                await channel.edit(slowmode_delay=int(BUMP_DELAY.total_seconds()))
                await start_timer(channel, time_remaining)
            break

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
        await handle_bump(bump_channel, message)
        return

    await bot.process_commands(message)

# === Gestion du bump ===
async def handle_bump(channel, message):
    # Vérifie l'heure exacte du dernier bump
    last_bump_time = message.created_at  # Heure du message de Disboard
    now = datetime.utcnow()

    # Calcule le temps restant pour le prochain bump possible
    time_elapsed = now - last_bump_time
    time_remaining = max(BUMP_DELAY - time_elapsed, timedelta(0))

    if time_remaining > timedelta(0):
        # Si un chrono est déjà actif, ne rien faire
        await channel.edit(topic=f"⏳ Prochain bump possible dans {format_time(time_remaining)}")
        return

    # Activer le mode lent pour 2 heures
    await channel.edit(slowmode_delay=int(BUMP_DELAY.total_seconds()))

    # Mettre à jour le sujet du salon avec un chrono
    await start_timer(channel, BUMP_DELAY)

# === Démarrage du chrono ===
async def start_timer(channel, duration):
    end_time = datetime.utcnow() + duration
    while datetime.utcnow() < end_time:
        remaining_time = end_time - datetime.utcnow()
        await channel.edit(topic=f"⏳ Prochain bump possible dans {format_time(remaining_time)}")
        await discord.utils.sleep_until(datetime.utcnow() + timedelta(seconds=1))

    # Désactiver le mode lent et notifier les utilisateurs
    await channel.edit(slowmode_delay=0, topic="✅ Le serveur peut être bump à nouveau !")
    await channel.send(f"<@&{BUMP_ROLE_ID}> 🎉 C'est le moment de bump le serveur !")

# === Utilitaire : Formatage du temps ===
def format_time(duration):
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Lancer le bot
bot.run(TOKEN)
