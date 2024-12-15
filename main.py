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

