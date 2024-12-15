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
    # Ignore les messages envoyés par le bot
    if message.author.bot:
        return

    # Gère la commande /bump
    if message.content == "/bump":
        bump_channel = discord.utils.get(message.guild.text_channels, name=BUMP_CHANNEL_NAME)

        # Si le message est envoyé dans le mauvais salon
        if message.channel != bump_channel:
            await message.delete()
            await message.author.send(f"📢 Vous ne pouvez bump que dans le salon {bump_channel.mention} !")
            return

        global last_bump_time
        now = datetime.utcnow()

        # Vérifie si le bump est encore en délai
        if last_bump_time and now - last_bump_time < BUMP_DELAY:
            remaining_time = BUMP_DELAY - (now - last_bump_time)
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await message.channel.send(
                f"⏳ {message.author.mention}, vous devez attendre encore {minutes} minutes et {seconds} secondes avant de bump 😅 !"
            )
            return

        # Mettre à jour l'heure du dernier bump
        last_bump_time = now

        # Mettre à jour les données de bump
        if str(message.author.id) in bump_data:
            bump_data[str(message.author.id)]["count"] += 1
        else:
            bump_data[str(message.author.id)] = {"count": 1}

        # Sauvegarder les données
        save_bump_data()

        # Remercier l'utilisateur pour le bump et démarrer le compte à rebours
        bump_count = bump_data[str(message.author.id)]["count"]
        await message.channel.send(
            f"Merci {message.author.mention} d'avoir bump le serveur ! 🙏\n"
            f"Vous avez maintenant bump {bump_count} fois. 🏆"
        )

        # Bloquer le salon et afficher le compte à rebours
        countdown.start(message.channel)

    # Autoriser le bot à continuer de traiter d'autres commandes
    await bot.process_commands(message)

# === Tâche de compte à rebours ===
@tasks.loop(seconds=1, count=int(BUMP_DELAY.total_seconds()))
async def countdown(channel):
    remaining_time = BUMP_DELAY - timedelta(seconds=countdown.current_loop)
    minutes, seconds = divmod(remaining_time.seconds, 60)
    await channel.edit(topic=f"⏳ Prochain bump possible dans {minutes} minutes et {seconds} secondes !")

    if countdown.current_loop == countdown.max_loops - 1:
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
