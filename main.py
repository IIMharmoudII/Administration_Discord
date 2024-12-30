import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('YOUR_DISCORD_BOT_TOKEN')

# Initialisation du bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)

# ID des rôles mutés et des canaux
MUTED_CHAT_ROLE_ID = '1323328422167969902'
MUTED_VOCAL_ROLE_ID = '1323339932206501970'
MUTED_CHANNEL_ID = '1323328820085919825'
RANK_DERANK_CHANNEL_ID = '1323247836518678590'

ROLE_HIERARCHY = [
    1312432497975627816,  # perm1
    1312432497027711036,  # perm2
    1312432496641703986,  # perm3
    1312432490392326305,  # perm4
    1312432489872097300,  # perm5
    1312432488823652392,  # 🎱
    1312432488353632296,  # 🧿
    1312432487175159808,  # 🔑
    1312427749981552690,  # ・Staff
    1312427747171369103,  # ・GS
    1312427543843835914,  # ・Modération
    1312426671152042055,  # ・GM
    1312432486604734494,  # Co-Owner
    1312432485472276490,  # Owner
    1316817785992511572,  # ✨
    1312422534607667210,  # ғя
    1312875389261054042,  # ・Dév
    1312435269466722345,  # PA
    1312420860283322449,  # 🧸
    1312420794525024306   # Couronne
]

# Vérifier si un rôle est supérieur ou égal dans la hiérarchie
def is_higher_role(executor: discord.Member, target: discord.Member):
    executor_roles = [r.id for r in executor.roles]
    target_roles = [r.id for r in target.roles]

    # Déterminer le rôle le plus élevé de chaque utilisateur
    executor_highest = min((ROLE_HIERARCHY.index(r) for r in executor_roles if r in ROLE_HIERARCHY), default=float('inf'))
    target_highest = min((ROLE_HIERARCHY.index(r) for r in target_roles if r in ROLE_HIERARCHY), default=float('inf'))

    # Logs pour vérifier la hiérarchie
    print(f"Executor roles: {executor_roles}, highest index: {executor_highest}")
    print(f"Target roles: {target_roles}, highest index: {target_highest}")

    return executor_highest < target_highest
    
# Événement déclenché quand le bot est prêt
@bot.event
async def on_ready():
    print(f"Bot prêt! Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()  # Synchronise les commandes slash avec Discord
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur de synchronisation : {e}")

# Commande slash pour mute chat
@bot.tree.command(name="mutechat", description="Mute un membre dans le chat pour une durée spécifiée")
async def mutechat(interaction: discord.Interaction, member: discord.Member, time: str, reason: str = "Aucune raison donnée"):
    guild = interaction.guild

    # Récupérer le rôle "muted chat" et le canal
    muted_role = guild.get_role(int(MUTED_CHAT_ROLE_ID))
    muted_channel = bot.get_channel(int(MUTED_CHANNEL_ID))

    if not muted_role:
        await interaction.response.send_message("Le rôle muté (chat) est introuvable!", ephemeral=True)
        return

    if not muted_channel:
        await interaction.response.send_message("Le canal muté est introuvable!", ephemeral=True)
        return

    # Ajouter le rôle muté
    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"{member.mention} a été muté dans le chat pour {time} pour la raison: {reason}")

    # Convertir le temps en secondes
    try:
        if time.endswith(("s", "sec", "second")):
            time_seconds = int(time.rstrip("s").rstrip("sec").rstrip("second"))
        elif time.endswith(("m", "min", "minute")):
            time_seconds = int(time.rstrip("m").rstrip("min").rstrip("minute")) * 60
        elif time.endswith(("h", "hour")):
            time_seconds = int(time.rstrip("h").rstrip("hour")) * 3600
        else:
            await interaction.followup.send("Format de temps invalide! Utilisez s, m, ou h.", ephemeral=True)
            return
    except ValueError:
        await interaction.followup.send("Temps invalide! Assurez-vous d'utiliser un nombre suivi de s, m, ou h.", ephemeral=True)
        return

    # Envoyer un message dans le canal muté
    if muted_channel:
        await muted_channel.send(
            f" **--------------------------------------------------**\n"
            f":no_entry: **Membre:** {member.mention}\n"
            f":timer: **Durée:** {time}\n"
            f":pencil: **Raison:** {reason}\n"
            f":medal: **STAFF:** {interaction.user.mention}\n"
            f"⚖️ **SANCTIONS : mute chat**"
        )

    # Attendre le temps spécifié
    try:
        await asyncio.sleep(time_seconds)
    except Exception as e:
        if muted_channel:
            await muted_channel.send(f"Erreur pendant l'attente : {e}")
        return

    # Retirer le rôle muté
    try:
        await member.remove_roles(muted_role, reason="Fin de la période de mute")
        if muted_channel:
            await muted_channel.send(f"{member.mention} n'est plus muté dans le chat.")
    except discord.Forbidden:
        if muted_channel:
            await muted_channel.send("Le bot n'a pas les permissions nécessaires pour retirer le rôle muté.")
    except Exception as e:
        if muted_channel:
            await muted_channel.send(f"Erreur inattendue lors de la suppression du rôle : {e}")

# Commande slash pour mute vocal
@bot.tree.command(name="mutevocal", description="Mute un membre dans le vocal pour une durée spécifiée")
async def mutevocal(interaction: discord.Interaction, member: discord.Member, time: str, reason: str = "Aucune raison donnée"):
    guild = interaction.guild

    # Récupérer le rôle "muted vocal" et le canal
    muted_role = guild.get_role(int(MUTED_VOCAL_ROLE_ID))
    muted_channel = bot.get_channel(int(MUTED_CHANNEL_ID))

    if not muted_role:
        await interaction.response.send_message("Le rôle muté (vocal) est introuvable!", ephemeral=True)
        return

    if not muted_channel:
        await interaction.response.send_message("Le canal muté est introuvable!", ephemeral=True)
        return

    # Ajouter le rôle muté
    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"{member.mention} a été muté dans le vocal pour {time} pour la raison: {reason}")

    # Convertir le temps en secondes
    try:
        if time.endswith(("s", "sec", "second")):
            time_seconds = int(time.rstrip("s").rstrip("sec").rstrip("second"))
        elif time.endswith(("m", "min", "minute")):
            time_seconds = int(time.rstrip("m").rstrip("min").rstrip("minute")) * 60
        elif time.endswith(("h", "hour")):
            time_seconds = int(time.rstrip("h").rstrip("hour")) * 3600
        else:
            await interaction.followup.send("Format de temps invalide! Utilisez s, m, ou h.", ephemeral=True)
            return
    except ValueError:
        await interaction.followup.send("Temps invalide! Assurez-vous d'utiliser un nombre suivi de s, m, ou h.", ephemeral=True)
        return

    # Envoyer un message dans le canal muté
    if muted_channel:
        await muted_channel.send(
            f" **--------------------------------------------------**\n"
            f":no_entry: **Membre:** {member.mention}\n"
            f":timer: **Durée:** {time}\n"
            f":pencil: **Raison:** {reason}\n"
            f":medal: **STAFF:** {interaction.user.mention}\n"
            f"⚖️ **SANCTIONS : mute vocal**"
        )

    # Attendre le temps spécifié
    try:
        await asyncio.sleep(time_seconds)
    except Exception as e:
        if muted_channel:
            await muted_channel.send(f"Erreur pendant l'attente : {e}")
        return

    # Retirer le rôle muté
    try:
        await member.remove_roles(muted_role, reason="Fin de la période de mute")
        if muted_channel:
            await muted_channel.send(f"{member.mention} n'est plus muté dans le vocal.")
    except discord.Forbidden:
        if muted_channel:
            await muted_channel.send("Le bot n'a pas les permissions nécessaires pour retirer le rôle muté.")
    except Exception as e:
        if muted_channel:
            await muted_channel.send(f"Erreur inattendue lors de la suppression du rôle : {e}")

# Gérer les erreurs (par exemple : permissions manquantes ou arguments invalides)
@mutechat.error
async def mutechat_error(interaction: discord.Interaction, error):
    try:
        if interaction.response.is_done():
            await interaction.followup.send("Une erreur est survenue.", ephemeral=True)
        else:
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
    except discord.errors.InteractionResponded:
        pass

@mutevocal.error
async def mutevocal_error(interaction: discord.Interaction, error):
    try:
        if interaction.response.is_done():
            await interaction.followup.send("Une erreur est survenue.", ephemeral=True)
        else:
            await interaction.response.send_message("Une erreur est survenue.", ephemeral=True)
    except discord.errors.InteractionResponded:
        pass

# Commande slash pour rankup
@bot.tree.command(name="rankup", description="Rankup un membre au rôle supérieur")
async def rankup(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not is_higher_role(interaction.user, member):
        await interaction.response.send_message("Vous ne pouvez pas rankup quelqu'un avec un rôle supérieur ou égal au vôtre!", ephemeral=True)
        return

    guild = interaction.guild
    rank_channel = bot.get_channel(int(RANK_DERANK_CHANNEL_ID))

    # Trouver le rôle actuel et le rôle supérieur
    current_roles = [role for role in member.roles if role.id in ROLE_HIERARCHY]
    if not current_roles:
        await interaction.response.send_message("Ce membre n'a pas de rôle valable pour un rankup.", ephemeral=True)
        return

    current_role = max(current_roles, key=lambda r: ROLE_HIERARCHY.index(r.id))
    current_index = ROLE_HIERARCHY.index(current_role.id)

    if current_index == 0:
        await interaction.response.send_message("Ce membre a déjà le rôle le plus élevé!", ephemeral=True)
        return

    next_role_id = ROLE_HIERARCHY[current_index - 1]
    next_role = guild.get_role(next_role_id)

    # Appliquer le rankup
    await member.remove_roles(current_role, reason=reason)
    await member.add_roles(next_role, reason=reason)
    await interaction.response.send_message(f"{member.mention} a été rankup au rôle {next_role.name} pour la raison : {reason}.")

    if rank_channel:
        await rank_channel.send(
            f"🔺 **RANKUP** 🔺\n**Membre :** {member.mention}\n**Nouveau rôle :** {next_role.name}\n**Raison :** {reason}\n**Effectué par :** {interaction.user.mention}"
        )

# Commande slash pour derank
@bot.tree.command(name="derank", description="Derank un membre au rôle inférieur")
async def derank(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not is_higher_role(interaction.user, member):
        await interaction.response.send_message("Vous ne pouvez pas derank quelqu'un avec un rôle supérieur ou égal au vôtre!", ephemeral=True)
        return

    guild = interaction.guild
    rank_channel = bot.get_channel(int(RANK_DERANK_CHANNEL_ID))

    # Trouver le rôle actuel et le rôle inférieur
    current_roles = [role for role in member.roles if role.id in ROLE_HIERARCHY]
    if not current_roles:
        await interaction.response.send_message("Ce membre n'a pas de rôle valable pour un derank.", ephemeral=True)
        return

    current_role = max(current_roles, key=lambda r: ROLE_HIERARCHY.index(r.id))
    current_index = ROLE_HIERARCHY.index(current_role.id)

    if current_index == len(ROLE_HIERARCHY) - 1:
        await interaction.response.send_message("Ce membre a déjà le rôle le plus bas!", ephemeral=True)
        return

    lower_role_id = ROLE_HIERARCHY[current_index + 1]
    lower_role = guild.get_role(lower_role_id)

    # Appliquer le derank
    await member.remove_roles(current_role, reason=reason)
    await member.add_roles(lower_role, reason=reason)
    await interaction.response.send_message(f"{member.mention} a été derank au rôle {lower_role.name} pour la raison : {reason}.")

    if rank_channel:
        await rank_channel.send(
            f"🔻 **DERANK** 🔻\n**Membre :** {member.mention}\n**Nouveau rôle :** {lower_role.name}\n**Raison :** {reason}\n**Effectué par :** {interaction.user.mention}"
        )

# Lancer le bot avec le token sécurisé
bot.run(TOKEN)
