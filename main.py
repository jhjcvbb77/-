import discord
from discord.ext import commands, tasks
import asyncio
import re
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

time_units = {
    "Y": 60 * 60 * 24 * 365,
    "M": 60 * 60 * 24 * 30,
    "W": 60 * 60 * 24 * 7,
    "D": 60 * 60 * 24,
    "H": 60 * 60,
    "Min": 60
}

def parse_duration(duration_str):
    matches = re.findall(r'(\d+)(Y|M|W|D|H|Min)', duration_str)
    total_seconds = 0
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]
    return total_seconds

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def jail(ctx, member: discord.Member = None, duration: str = None, *, reason: str = None):
    if not member or not duration or not reason:
        return await ctx.send("❌ الاستخدام الصحيح: `!jail @user 10Min السبب`")

    seconds = parse_duration(duration)
    if seconds < 60:
        return await ctx.send("⛔ أقل مدة للسجن هي دقيقة واحدة.")

    jail_role = discord.utils.get(ctx.guild.roles, name="Saydnaya")
    if not jail_role:
        return await ctx.send("❌ رتبة 'Saydnaya' غير موجودة.")

    try:
        await member.add_roles(jail_role)
        await ctx.send(f"🚨 {member.mention} تم سجنه لمدة {duration} بسبب: {reason}")
        await member.send(f"📛 تم سجنك في **{ctx.guild.name}** لمدة {duration} بسبب: {reason}")

        await asyncio.sleep(seconds)

        await member.remove_roles(jail_role)
        await ctx.send(f"✅ {member.mention} انتهت مدة سجنه.")

    except Exception as e:
        await ctx.send(f"⚠️ خطأ: {str(e)}")

bot.run(os.getenv("DISCORD_TOKEN"))
