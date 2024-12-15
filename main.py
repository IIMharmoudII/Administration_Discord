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
bump_data = {}  # Stocke les informations de bump pour chaque utilisateur
last_bump_time = {}  # Stocke la dernière heure de bump pour chaque utilisateur
BUMP_DELAY = timedelta(hours=2)  # Délai entre deux bumps (2 heures)

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
            await message.author.send(f"\ud83d\udce2 Vous ne pouvez bump que dans le salon {bump_channel.mention} !")
            return

        # Gérer le délai de 2 heures
        now = datetime.utcnow()
        last_bump = last_bump_time.get(message.author.id)
        if last_bump and now - last_bump < BUMP_DELAY:
            remaining_time = BUMP_DELAY - (now - last_bump)
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await message.channel.send(
                f"\u23f3 {message.author.mention}, vous devez attendre encore {minutes} minutes et {seconds} secondes avant de bump \ud83d\ude05 !"
            )
            return

        # Mettre à jour les données de bump
        last_bump_time[message.author.id] = now
        if message.author.id in bump_data:
            bump_data[message.author.id]["count"] += 1
        else:
            bump_data[message.author.id] = {"count": 1}

        # Remercier l'utilisateur pour le bump
        bump_count = bump_data[message.author.id]["count"]
        await message.channel.send(
            f"Merci {message.author.mention} d'avoir bump le serveur ! \ud83d\ude4f\n"
            f"Vous avez maintenant bump {bump_count} fois. \ud83c\udfc6"
        )

    # Autoriser le bot à continuer de traiter d'autres commandes
    await bot.process_commands(message)

# === Commande : ?bump ===
@bot.command()
async def bump(ctx, member: discord.Member = None):
    if member:
        user_data = bump_data.get(member.id, {"count": 0})
        await ctx.send(f"{member.mention} a bump {user_data['count']} fois.")
    else:
        user_data = bump_data.get(ctx.author.id, {"count": 0})
        await ctx.send(f"{ctx.author.mention} Vous avez bump {user_data['count']} fois.")

# === Commande : ?bumpclassement ===
@bot.command()
async def bumpclassement(ctx):
    if not bump_data:
        await ctx.send("Personne n'a encore bump !")
        return

    classement = sorted(bump_data.items(), key=lambda x: x[1]["count"], reverse=True)
    message = "\ud83c\udfc6 **Classement des bumpers :**\n"
    for i, (user_id, data) in enumerate(classement[:10], start=1):
        user = await bot.fetch_user(user_id)
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
        "`/bump` : Utilisez cette commande pour bump le serveur (uniquement dans le salon \ud83d\udc96・bump)."
    )
    await ctx.send(help_message)

# Lancer le bot
bot.run(TOKEN)
