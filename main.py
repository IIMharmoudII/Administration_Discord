import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
import json
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
BUMP_DATA_FILE = "bump_data.json"  # Nom du fichier pour sauvegarder les données
bump_data = {}  # Stocke les informations de bump pour chaque utilisateur
last_bump_time = None  # Heure du dernier bump dans le salon
BUMP_DELAY = timedelta(hours=2)  # Délai entre deux bumps (2 heures)

# === Fonctions de sauvegarde et chargement ===
def load_bump_data():
    global bump_data
    try:
        with open(BUMP_DATA_FILE, 'r') as file:
            bump_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        bump_data = {}

def save_bump_data():
    with open(BUMP_DATA_FILE, 'w') as file:
        json.dump(bump_data, file)

# Charger les données au démarrage
load_bump_data()

# === Événement : Quand un message est envoyé ===
@bot.event
async def on_message(message):
    bump_channel = discord.utils.get(message.guild.text_channels, name=BUMP_CHANNEL_NAME)

    # Vérifier si le salon bump existe
    if not bump_channel:
        print(f"Erreur : Salon '{BUMP_CHANNEL_NAME}' introuvable.")
        return

    # Empêcher l'utilisation de `/bump` en dehors du salon désigné
    if message.channel != bump_channel and "/bump" in message.content.lower():
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, veuillez utiliser la commande `/bump` uniquement dans {bump_channel.mention} !",
            delete_after=5
        )
        return

    # Détecter le message de Disboard confirmant le bump
    if message.author.bot and message.author.id == 302050872383242240 and "Bump effectué !" in message.content:
        global last_bump_time
        now = datetime.utcnow()

        last_bump_time = now
        author_id = message.mentions[0].id if message.mentions else None

        if author_id and str(author_id) in bump_data:
            bump_data[str(author_id)]["count"] += 1
        elif author_id:
            bump_data[str(author_id)] = {"count": 1}

        save_bump_data()

        bump_count = bump_data[str(author_id)]["count"] if author_id else 0
        await bump_channel.send(
            f"Merci <@{author_id}> d'avoir bump le serveur ! 🙏\n"
            f"Vous avez maintenant bump {bump_count} fois. 🏆"
        )

        countdown.start(bump_channel)
        return

    await bot.process_commands(message)

# === Tâche de compte à rebours ===
@tasks.loop(seconds=1, count=int(BUMP_DELAY.total_seconds()))
async def countdown(channel):
    remaining_time = BUMP_DELAY - timedelta(seconds=countdown.current_loop)
    minutes, seconds = divmod(remaining_time.seconds, 60)

    if countdown.current_loop < countdown.max_loops - 1:
        await channel.edit(topic=f"⏳ Prochain bump possible dans {minutes} minutes et {seconds} secondes !")
    else:
        await channel.send(f"@everyone 🎉 Vous pouvez à nouveau bump le serveur ! Utilisez `/bump` maintenant !")
        await channel.edit(topic="✅ Le serveur peut être bump à nouveau !")

# === Commande : ?bump ===
@bot.command()
async def bump(ctx, member: discord.Member = None):
    if member:
        user_data = bump_data.get(str(member.id), {"count": 0})
        await ctx.send(f"{member.mention} a bump {user_data['count']} fois.")
    else:
        user_data = bump_data.get(str(ctx.author.id), {"count": 0})
        await ctx.send(f"{ctx.author.mention} Vous avez bump {user_data['count']} fois.")

# === Commande : ?bumpclassement ===
@bot.command()
async def bumpclassement(ctx):
    if not bump_data:
        await ctx.send("Personne n'a encore bump !")
        return

    classement = sorted(bump_data.items(), key=lambda x: x[1]["count"], reverse=True)
    message = "🏆 **Classement des bumpers :**\n"
    for i, (user_id, data) in enumerate(classement[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        message += f"{i}. {user.mention} - {data['count']} bumps\n"
    await ctx.send(message)

# === Commande : ?help ===
@bot.command()
async def help(ctx):
    help_message = (
        "**Commandes disponibles :**\n"
        "`?bump` : Affiche le nombre de bumps que vous avez effectués.\n"
        "`?bump @utilisateur` : Affiche le nombre de bumps effectués par un utilisateur.\n"
        "`?bumpclassement` : Affiche le classement des personnes ayant le plus bump.\n"
        "`/bump` : Utilisez cette commande pour bump le serveur (uniquement dans le salon 💖・bump)."
    )
    await ctx.send(help_message)

# Lancer le bot
bot.run(TOKEN)
