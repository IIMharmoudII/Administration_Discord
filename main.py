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
    "perm1": 123456789012345678,
    "perm2": 123456789012345679,
    "perm3": 123456789012345680,
    "perm4": 123456789012345681,
    "perm5": 123456789012345682,
    "staff": 123456789012345683,
    "moderation": 123456789012345684,
    "logs": 123456789012345685
}

# Limites de temps pour les mutes par rôle
MUTE_LIMITS = {
    "perm1": 10,
    "perm2": 15,
    "perm3": 20,
    "perm4": 25,
    "perm5": 30,
    "staff": 60,
    "moderation": 120
}

# Fonction pour vérifier les permissions
def has_permission(ctx, target_member):
    user_roles = [role.id for role in ctx.author.roles]
    target_roles = [role.id for role in target_member.roles]

    # Comparer la hiérarchie des rôles
    for role_id in sorted(ROLE_IDS.values(), reverse=True):
        if role_id in user_roles:
            if role_id not in target_roles:
                return True
            else:
                return False
    return False

# === Classe pour le Modal de mute ===
class MuteModal(Modal):
    def __init__(self, max_time, member, *args, **kwargs):
        super().__init__(title="Mute Form", *args, **kwargs)
        self.max_time = max_time
        self.member = member

        self.duration = TextInput(
            label="Durée (minutes)",
            placeholder=f"Maximum {self.max_time} minutes",
            required=True
        )
        self.reason = TextInput(
            label="Raison",
            placeholder="Motif du mute",
            required=True
        )

        self.add_item(self.duration)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            duration = int(self.duration.value)
            if duration > self.max_time:
                await interaction.response.send_message(
                    f"Durée invalide. Maximum autorisé : {self.max_time} minutes.",
                    ephemeral=True
                )
                return

            reason = self.reason.value
            await self.member.timeout(
                discord.utils.utcnow() + discord.timedelta(minutes=duration),
                reason=reason
            )
            await interaction.response.send_message(
                f"{self.member.mention} a été mute pendant {duration} minutes. Raison : {reason}"
            )
        except ValueError:
            await interaction.response.send_message(
                "Durée invalide. Veuillez entrer un nombre entier.",
                ephemeral=True
            )

# === Commandes du bot ===
@bot.command()
async def mute(ctx, member: discord.Member, max_time: int):
    if not has_permission(ctx, member):
        await ctx.send(f"Vous n'avez pas la permission de mute {member.mention}.")
        return

    max_time = MUTE_LIMITS.get(ctx.author.top_role.id, 10)
    modal = MuteModal(max_time=max_time, member=member)
    await ctx.send_modal(modal)

@bot.command()
async def rankup(ctx, member: discord.Member, *, reason: str):
    if not has_permission(ctx, member):
        await ctx.send(f"Vous n'avez pas la permission de promouvoir {member.mention}.")
        return

    current_role = max(member.roles, key=lambda role: role.position)
    new_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS["perm5"])  # Rôle cible

    if new_role and current_role != new_role:
        await member.remove_roles(current_role)
        await member.add_roles(new_role)
        await ctx.send(f"{member.mention} a été promu à {new_role.name}. Raison : {reason}")
    else:
        await ctx.send(f"{member.mention} a déjà le rôle {new_role.name}.")

@bot.command()
async def derank(ctx, member: discord.Member, *, reason: str):
    if not has_permission(ctx, member):
        await ctx.send(f"Vous n'avez pas la permission de rétrograder {member.mention}.")
        return

    current_role = max(member.roles, key=lambda role: role.position)
    new_role = discord.utils.get(ctx.guild.roles, id=ROLE_IDS["perm4"])  # Rôle cible

    if new_role and current_role != new_role:
        await member.remove_roles(current_role)
        await member.add_roles(new_role)
        await ctx.send(f"{member.mention} a été rétrogradé à {new_role.name}. Raison : {reason}")
    else:
        await ctx.send(f"{member.mention} a déjà le rôle {new_role.name}.")

# Démarrer le serveur web et le bot
keep_alive()
bot.run(TOKEN)
