import discord
from discord import app_commands
from discord.ext import tasks
import asyncio
import re
import os

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

JAIL_ROLE_NAME = "Saydnaya"
MOD_ROLE_NAME = "jail mod"
WARNINGS = {}

time_multipliers = {
    "y": 60 * 60 * 24 * 365,
    "m": 60 * 60 * 24 * 30,
    "w": 60 * 60 * 24 * 7,
    "d": 60 * 60 * 24,
    "h": 60 * 60,
    "min": 60
}

def parse_duration(duration_str):
    match = re.fullmatch(r"(\d+)(y|m|w|d|h|min)", duration_str.lower())
    if not match:
        return None
    amount, unit = match.groups()
    return int(amount) * time_multipliers[unit]

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

@tree.command(name="setup", description="إنشاء رتبة صيدنايا وروم السجن تلقائيًا")
async def setup(interaction: discord.Interaction):
    guild = interaction.guild

    jail_role = discord.utils.get(guild.roles, name=JAIL_ROLE_NAME)
    if not jail_role:
        jail_role = await guild.create_role(name=JAIL_ROLE_NAME)
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        jail_role: discord.PermissionOverwrite(view_channel=True, send_messages=False)
    }

    jail_channel = discord.utils.get(guild.text_channels, name="سجن")
    if not jail_channel:
        jail_channel = await guild.create_text_channel("سجن", overwrites=overwrites)
    
    await interaction.response.send_message("✅ تم إنشاء رتبة وروم السجن بنجاح!", ephemeral=True)

@tree.command(name="jail", description="سجن عضو لمدة معينة")
@app_commands.describe(member="العضو المراد سجنه", duration="المدة (مثال: 10min)", reason="السبب")
async def jail(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):
    if not interaction.user.guild_permissions.administrator and MOD_ROLE_NAME not in [r.name for r in interaction.user.roles]:
        return await interaction.response.send_message("❌ ما عندك صلاحية تسجن.", ephemeral=True)

    seconds = parse_duration(duration)
    if seconds is None or seconds < 60:
        return await interaction.response.send_message("⚠️ أقل مدة للسجن هي 1 دقيقة. واستخدم: y, m, w, d, h, min", ephemeral=True)

    jail_role = discord.utils.get(interaction.guild.roles, name=JAIL_ROLE_NAME)
    if not jail_role:
        jail_role = await interaction.guild.create_role(name=JAIL_ROLE_NAME)

    await member.add_roles(jail_role, reason=reason)
    await interaction.response.send_message(f"🚨 {member.mention} تم سجنه لمدة {duration} بسبب: {reason}")

    WARNINGS[member.id] = WARNINGS.get(member.id, 0) + 1
    await interaction.channel.send(f"⚠️ {member.mention} أخذ إنذار. المجموع: {WARNINGS[member.id]}")

    await asyncio.sleep(seconds)
    await member.remove_roles(jail_role, reason="انتهت مدة السجن")
    await interaction.channel.send(f"🔓 {member.mention} خرج من السجن.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
