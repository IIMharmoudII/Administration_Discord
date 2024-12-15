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

# Initialisation du bot
bot = commands.Bot(command_prefix="?", intents=intents)

# Variables globales
bump_data = {}
bump_channel_name = "💞・bump"
bump_cooldown = timedelta(hours=2)

# === Gestion des événements ===
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("/bump"):
        channel = message.channel
        if channel.name != bump_channel_name:
            await message.delete()
            await channel.send(f"{message.author.mention} Merci de bump uniquement dans le salon {bump_channel_name}.", delete_after=5)
            return

        now = datetime.utcnow()
        user_data = bump_data.get(message.author.id, {"last_bump": None, "count": 0})
        last_bump = user_data["last_bump"]

        if last_bump and now - last_bump < bump_cooldown:
            remaining = bump_cooldown - (now - last_bump)
            await channel.send(f"{message.author.mention} Vous pouvez bump à nouveau dans {remaining.seconds // 3600}h{(remaining.seconds // 60) % 60}m.")
            return

        # Mettre à jour les données de bump
        user_data["last_bump"] = now
        user_data["count"] += 1
        bump_data[message.author.id] = user_data

        await channel.send(f"Merci {message.author.mention} d'avoir bump le serveur ! 🎉 Nombre total de bumps : {user_data['count']}.")

    await bot.process_commands(message)

# === Commandes ===
@bot.command()
async def bump(ctx, member: discord.Member = None):
    if member:
        user_data = bump_data.get(member.id, {"count": 0})
        await ctx.send(f"{member.mention} a bump {user_data['count']} fois.")
    else:
        user_data = bump_data.get(ctx.author.id, {"count": 0})
        await ctx.send(f"{ctx.author.mention} Vous avez bump {user_data['count']} fois.")

@bot.command()
async def bumpclassement(ctx):
    if not bump_data:
        await ctx.send("Personne n'a encore bump !")
        return

    classement = sorted(bump_data.items(), key=lambda x: x[1]["count"], reverse=True)
    message = "🏆 **Classement des bumpers :**\n"
    for i, (user_id, data) in enumerate(classement[:10], start=1):
        user = await bot.fetch_user(user_id)
        message += f"{i}. {user.mention} - {data['count']} bumps\n"
    await ctx.send(message)

@bot.command()
async def help(ctx):
    help_message = (
        "**Commandes disponibles :**\n"
        "`?bump` : Affiche le nombre de bumps que vous avez effectués.\n"
        "`?bump @utilisateur` : Affiche le nombre de bumps effectués par un utilisateur.\n"
        "`?bumpclassement` : Affiche le classement des personnes ayant le plus bump.\n"
        "`/bump` : Utilisez cette commande pour bump le serveur (uniquement dans le salon {bump_channel_name})."
    )
    await ctx.send(help_message)

# Lancer le bot
bot.run(TOKEN)

