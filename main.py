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

# Commande pour derank
@bot.command()
async def derank(ctx, member: discord.Member, reason: str = None):
    if not reason:
        await ctx.send("Tu dois spécifier une raison à la suite de la commande.\nExemple : `+derank @Merguez pour mauvaise conduite`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de retirer un rôle à {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    # Retirer un rôle spécifique du membre
    current_role = max(member.roles, key=lambda r: r.position)
    lower_roles = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
    for role in lower_roles:
        if role.position < current_role.position:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} a perdu le rôle {role.name} pour la raison : {reason}.")
            return
    await ctx.send(f"{member.mention} n'a pas de rôle inférieur à celui-ci.")

# Commande pour rankup
@bot.command()
async def rankup(ctx, member: discord.Member, reason: str = None):
    if not reason:
        await ctx.send("Tu dois spécifier une raison à la suite de la commande.\nExemple : `+rankup @Merguez pour bon comportement`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de rankup {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    # Suppression de l'ancien rôle et ajout du nouveau
    current_role = max(member.roles, key=lambda r: r.position)
    new_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS["perm5"])  # Exemple pour ajouter perm5

    if current_role != new_role:
        await member.remove_roles(current_role)
        await member.add_roles(new_role)
        await ctx.send(f"{member.mention} a été promu à {new_role.name}.")
    else:
        await ctx.send(f"{member.mention} a déjà le rôle {new_role.name}.")

# Commande pour mutechat
@bot.command()
async def mutechat(ctx, member: discord.Member, time: str, reason: str):
    if not time or not reason:
        await ctx.send("Tu dois spécifier la durée et la raison à la suite de la commande.\nExemple : `+mutechat @Merguez 20m troll`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission de mute {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    # Validation de la durée
    if time.endswith('m'):
        minutes = int(time[:-1])  # Extraction des minutes
    elif time.endswith('h'):
        minutes = int(time[:-1]) * 60  # Conversion des heures en minutes
    else:
        await ctx.send("Le format du temps est invalide. Utilisez 'm' pour minutes et 'h' pour heures.")
        return

    avert_channel = ctx.guild.get_channel(ROLE_IDS["avertissements"])
    await avert_channel.send(f"{member.mention} a été mute dans le chat pour {minutes} minutes. Raison : {reason}.")
    await ctx.send(f"{member.mention} a été mute dans le chat pour {minutes} minutes. Raison : {reason}.")

# Commande pour avertir
@bot.command()
async def avert(ctx, member: discord.Member, reason: str = None):
    if not reason:
        await ctx.send("Tu dois spécifier une raison à la suite de la commande.\nExemple : `+avert @Merguez troll`")
        return

    if not has_permission(ctx, member):
        await ctx.send(f"Tu n'as pas la permission d'avertir {member.mention} car il a un rôle supérieur ou égal au tien.")
        return

    avert_channel = ctx.guild.get_channel(ROLE_IDS["avertissements"])
    await avert_channel.send(f"**Avertissement:** {ctx.author.mention} a averti {member.mention} pour : {reason}.")
    await ctx.send(f"Avertissement envoyé à {member.mention} avec la raison : {reason}.")

# Lancer le bot et garder le serveur en ligne
keep_alive()
bot.run(TOKEN)
