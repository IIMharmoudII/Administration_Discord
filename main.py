import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('YOUR_DISCORD_BOT_TOKEN')

# Configurer les intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialisation du bot
bot = commands.Bot(command_prefix="+", intents=intents)

# === Serveur Web pour garder le bot actif ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ID des rôles et catégories
ROLE_IDS = {
    "perm1": 1312432497975627816,
    "perm2": 1312432497027711036,
    "perm3": 1312432496641703986,
    "perm4": 1312432490392326305,
    "perm5": 1312432489872097300,
    "staff": 1312427749981552690,
    "gs": 1312427747171369103,
    "moderation": 1312427543843835914,
    "gm": 1312426671152042055,
    "owner": 1312432485472276490,
    "co_owner": 1312432486604734494,
    "logs": 1312414690172735508,
    "staff_info": 1312414623802196071,
    "bans": 1323247686660526111,
    "avertissements": 1323247758186123335,
    "rank_derank": 1323247836518678590,
    "couronne": 1312420794525024306  # Rôle de la couronne
}

# Limites de temps pour les mutes par rôle
MUTE_LIMITS = {
    "perm1": 10,
    "perm2": 15,
    "perm3": 20,
    "perm4": 25,
    "perm5": 30,
    "staff": 60,
    "gs": 120,
    "moderation": 240,
    "gm": 480,
    "co_owner": 50,
    "owner": 60
}

# Fonction pour vérifier si l'utilisateur a les permissions nécessaires
def has_permission(ctx, target_member):
    user_roles = [role.id for role in ctx.author.roles]
    target_roles = [role.id for role in target_member.roles]
    
    # On vérifie si l'utilisateur a un rôle plus élevé dans la hiérarchie que la cible
    for role_id in sorted(ROLE_IDS.values(), reverse=True):
        if role_id in user_roles:
            # L'utilisateur doit avoir un rôle plus élevé que la cible
            if any(role.id in target_roles for role in ctx.guild.roles):
                return True
            else:
                return False
    return False

# Classe pour le modal de mute
class MuteModal(Modal):
    def __init__(self, max_time, member, action_type, *args, **kwargs):
        super().__init__(title=f"{action_type} Modal", *args, **kwargs)
        self.max_time = max_time
        self.member = member
        self.action_type = action_type

        # Champs de saisie
        self.duration_input = TextInput(
            label=f"Durée du {action_type} (en minutes)",
            placeholder=f"Max : {max_time} minutes",
            required=True
        )
        self.reason_input = TextInput(
            label="Raison",
            placeholder="Indiquez la raison du mute ou de l'avertissement",
            required=True
        )
        self.add_item(self.duration_input)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            duration = int(self.duration_input.value)
            if duration > self.max_time:
                await interaction.response.send_message(
                    f"Vous ne pouvez pas {self.action_type.lower()} pour plus de {self.max_time} minutes.",
                    ephemeral=True
                )
                return

            reason = self.reason_input.value

            if self.action_type == "Mute":
                await self.member.timeout(
                    discord.utils.utcnow() + discord.timedelta(minutes=duration),
                    reason=reason
                )
                await interaction.response.send_message(
                    f"{self.member.mention} a été mute pour {duration} minutes. Raison : {reason}"
                )
            else:  # Pour avertissements
                avert_channel = interaction.guild.get_channel(ROLE_IDS["avertissements"])
                await avert_channel.send(
                    f"**Avertissement:** {interaction.user.mention} a averti {self.member.mention} pour : {reason}. "
                    f"Durée : {duration} minutes. (Premier avertissement si applicable)"
                )
                await interaction.response.send_message(
                    f"Avertissement envoyé à {self.member.mention} avec la raison : {reason}.",
                    ephemeral=True
                )
        except ValueError:
            await interaction.response.send_message(
                "Veuillez entrer une durée valide.",
                ephemeral=True
            )

# Commande pour rankup
@bot.command()
async def rankup(ctx, member: discord.Member = None, *, reason: str = None):
    if not member or not reason:
        await ctx.send("Tu dois spécifier un membre et une raison pour la commande. Exemple : `+rankup @Merguez pour bon comportement`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de rankup {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    current_role = max(member.roles, key=lambda r: r.position)
    new_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS["perm5"])  # Exemple pour ajouter perm5

    if current_role != new_role:
        await member.remove_roles(current_role)
        await member.add_roles(new_role)
        await ctx.send(f"{member.mention} a été promu à {new_role.name}.")
    else:
        await ctx.send(f"{member.mention} a déjà le rôle {new_role.name}.")

# Commande pour derank
@bot.command()
async def derank(ctx, member: discord.Member = None, *, reason: str = None):
    if not member or not reason:
        await ctx.send("Tu dois spécifier un membre et une raison pour la commande. Exemple : `+derank @Merguez pour comportement inapproprié`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de derank {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    current_role = max(member.roles, key=lambda r: r.position)
    new_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS["perm4"])  # Exemple pour retirer perm5

    if current_role != new_role:
        await member.remove_roles(current_role)
        await member.add_roles(new_role)
        await ctx.send(f"{member.mention} a été rétrogradé à {new_role.name}.")
    else:
        await ctx.send(f"{member.mention} a déjà le rôle {new_role.name}.")

# Commande pour avertir
@bot.command()
async def avert(ctx, member: discord.Member = None, *, reason: str = None):
    if not member or not reason:
        await ctx.send("Tu dois spécifier un membre et une raison pour la commande. Exemple : `+avert @Merguez pour troll`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission d'avertir {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    avert_channel = ctx.guild.get_channel(ROLE_IDS["avertissements"])
    await avert_channel.send(f"**Avertissement:** {ctx.author.mention} a averti {member.mention} pour : {reason}.")
    await ctx.send(f"Avertissement envoyé à {member.mention} avec la raison : {reason}.")

# Commande pour mutechat
@bot.command()
async def mutechat(ctx, member: discord.Member = None, time: str = None, *, reason: str = None):
    if not member or not time or not reason:
        await ctx.send("Tu dois spécifier un membre, un temps (en minutes ou heures) et une raison. Exemple : `+mutechat @Merguez 20m pour spam`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de mute {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    try:
        if time.endswith('m'):
            minutes = int(time[:-1])
        elif time.endswith('h'):
            hours = int(time[:-1])
            minutes = hours * 60
        else:
            raise ValueError
    except ValueError:
        await ctx.send("Le format du temps est invalide. Utilise 'm' pour minutes et 'h' pour heures.")
        return

    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"{member.mention} a été mute pour {minutes} minutes. Raison : {reason}.")

# Commande pour mute vocal
@bot.command()
async def mutevocal(ctx, member: discord.Member = None, time: str = None, *, reason: str = None):
    if not member or not time or not reason:
        await ctx.send("Tu dois spécifier un membre, un temps (en minutes ou heures) et une raison. Exemple : `+mutevocal @Merguez 20m pour troll`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de mute vocal {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    try:
        if time.endswith('m'):
            minutes = int(time[:-1])
        elif time.endswith('h'):
            hours = int(time[:-1])
            minutes = hours * 60
        else:
            raise ValueError
    except ValueError:
        await ctx.send("Le format du temps est invalide. Utilise 'm' pour minutes et 'h' pour heures.")
        return

    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"{member.mention} a été mute dans le vocal pour {minutes} minutes. Raison : {reason}.")

# Commande pour afficher la liste des commandes
@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title="Liste des commandes disponibles",
        description="Voici les commandes disponibles sur ce serveur.",
        color=discord.Color.green()
    )

    embed.add_field(name="+rankup", value="Promouvoir un utilisateur à un rôle supérieur. Exemple : `+rankup @Merguez pour bon comportement`")
    embed.add_field(name="+derank", value="Rétrograder un utilisateur à un rôle inférieur. Exemple : `+derank @Merguez pour comportement inapproprié`")
    embed.add_field(name="+mutechat", value="Mute un utilisateur dans le chat. Exemple : `+mutechat @Merguez 20m pour spam`")
    embed.add_field(name="+mutevocal", value="Mute un utilisateur dans le vocal. Exemple : `+mutevocal @Merguez 10m pour troll`")
    embed.add_field(name="+avert", value="Avertir un utilisateur. Exemple : `+avert @Merguez pour comportement mauvais`")

    await ctx.send(embed=embed)

# Lancer le bot
keep_alive()
bot.run(TOKEN)
