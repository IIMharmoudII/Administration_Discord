import discord
from discord.ext import commands
from discord.ui import Modal, TextInput

# Configuration de base du bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

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
    "staff_info": 1312414623802196071
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

class MuteModal(Modal):
    def __init__(self, max_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_time = max_time
        self.add_item(InputText(label="Durée du mute (en minutes)", placeholder=f"Max : {max_time} minutes"))
        self.add_item(InputText(label="Raison du mute", placeholder="Indiquez la raison"))

    async def callback(self, interaction: discord.Interaction):
        try:
            duration = int(self.children[0].value)
            if duration > self.max_time:
                await interaction.response.send_message(f"Vous ne pouvez pas mute pour plus de {self.max_time} minutes.", ephemeral=True)
                return

            reason = self.children[1].value
            user = interaction.message.mentions[0]
            await interaction.guild.timeout(user, duration * 60, reason=reason)
            await interaction.response.send_message(f"{user.mention} a été mute pour {duration} minutes. Raison : {reason}")
        except ValueError:
            await interaction.response.send_message("Veuillez entrer une durée valide.", ephemeral=True)

# Commande pour mute
@bot.command()
async def mutevocal(ctx, member: discord.Member):
    user_roles = [role.id for role in ctx.author.roles]
    for role, max_time in MUTE_LIMITS.items():
        if ROLE_IDS[role] in user_roles:
            modal = MuteModal(max_time, title="Mute Vocal")
            await ctx.send(f"{ctx.author.mention}, veuillez remplir les informations pour muter {member.mention}.", view=modal)
            return

    await ctx.send("Vous n'avez pas la permission de mute.")

@bot.command()
async def rankup(ctx, member: discord.Member):
    user_roles = [role.id for role in ctx.author.roles]
    member_roles = [role.id for role in member.roles]

    for role in ROLE_IDS.keys():
        if ROLE_IDS[role] in user_roles:
            next_role_id = get_next_role(role)
            if next_role_id and next_role_id not in member_roles:
                role_to_add = ctx.guild.get_role(next_role_id)
                await member.add_roles(role_to_add)
                await ctx.send(f"{member.mention} a été promu au rôle {role_to_add.name}.")
                return

    await ctx.send("Impossible de promouvoir cet utilisateur.")

@bot.command()
async def derank(ctx, member: discord.Member):
    user_roles = [role.id for role in ctx.author.roles]
    member_roles = [role.id for role in member.roles]

    for role in ROLE_IDS.keys():
        if ROLE_IDS[role] in user_roles:
            previous_role_id = get_previous_role(role)
            if previous_role_id and previous_role_id in member_roles:
                role_to_remove = ctx.guild.get_role(previous_role_id)
                await member.remove_roles(role_to_remove)
                await ctx.send(f"{member.mention} a été rétrogradé et a perdu le rôle {role_to_remove.name}.")
                return

    await ctx.send("Impossible de rétrograder cet utilisateur.")

# Fonction pour récupérer le rôle suivant
def get_next_role(current_role):
    roles = list(ROLE_IDS.keys())
    try:
        current_index = roles.index(current_role)
        return ROLE_IDS[roles[current_index + 1]] if current_index + 1 < len(roles) else None
    except ValueError:
        return None

# Fonction pour récupérer le rôle précédent
def get_previous_role(current_role):
    roles = list(ROLE_IDS.keys())
    try:
        current_index = roles.index(current_role)
        return ROLE_IDS[roles[current_index - 1]] if current_index > 0 else None
    except ValueError:
        return None

@bot.command()
async def avert(ctx, member: discord.Member):
    modal = MuteModal(max_time=0, title="Avertissement")  # Pas de durée limite pour avert
    await ctx.send(f"{ctx.author.mention}, veuillez remplir les informations pour avertir {member.mention}.", view=modal)

# Démarrage du bot
bot.run("BOT_TOKEN")
