import asyncio
import datetime
import logging
import os

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from putergenai import PuterClient

# ---------- Konfiguration ----------
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("ERROR: No token found in environment variables!")
    exit(1)

# Eigene Konfigurationsdatei für HaMy-Features
import config

# ---------- Logging Setup ----------
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if message.guild:
        server_name = message.guild.name
        server_id = message.guild.id
        channel_name = message.channel.name
        channel_id = message.channel.id
        location_info = f"[Server: {server_name} ({server_id}) | Channel: #{channel_name} ({channel_id})]"
    else:
        server_name = "DM"
        server_id = "N/A"
        channel_name = "Direct Message"
        channel_id = message.channel.id
        location_info = f"[DM with {message.author} | Channel ID: {channel_id}]"
    log_entry = f'[{timestamp}] {location_info} {message.author} ({message.author.id}): "{message.content}"\n'
    with open('messages.log', 'a', encoding='utf-8') as f:
        f.write(log_entry)

# ---------- Bot Setup ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='§', intents=intents)

# ---------- Hilfsfunktion für AI ----------
async def deepseek(set_prompt, set_model):
    async with PuterClient() as client:
        await client.login("verplanter", "Ichbinder1.")
        result = await client.ai_chat(
            prompt=set_prompt,
            options={"model": set_model if set_model else "gpt-4o", "stream": False}
        )
        return result["response"]["result"]["message"]["content"]

# ---------- Bot Events ----------
@bot.event
async def on_ready():
    print(f'✅ Eingeloggt als {bot.user} (ID: {bot.user.id})')
    
    # Slash Commands synchronisieren
    if config.GUILD_ID:
        guild = discord.Object(id=config.GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        try:
            await bot.tree.sync(guild=guild)
            print(f"✅ Slash Commands für Server {config.GUILD_ID} synchronisiert.")
        except discord.Forbidden:
            print("❌ 403 Forbidden – Bot muss mit 'applications.commands' Scope neu eingeladen werden!")
    else:
        print("⚠️ GUILD_ID nicht gesetzt – keine Slash-Command-Synchronisation.")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="@ha.my07_ auf TikTok"
        )
    )
    print("=== Bot ist bereit! ===")

@bot.event
async def on_message(message):
    log_message(message)

    if message.author.bot:
        await bot.process_commands(message)
        return

    # DM Antwort mit AI
    if message.guild is None and message.author != bot.user:
        try:
            if message.content.startswith(bot.command_prefix):
                await bot.process_commands(message)
                return

            if not message.content.strip():
                response = "Hallo! Du hast eine leere Nachricht gesendet."
            else:
                response = await deepseek(message.content, "deepseek-chat")
                if len(response) > 2000:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"response_{timestamp}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response)
                    await message.channel.send(
                        "Antwort zu lang – hier als Datei:",
                        file=discord.File(filename)
                    )
                    os.remove(filename)
                else:
                    await message.channel.send(response)

            # Logge Bot-Antwort
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f'[{timestamp}] [DM Response to {message.author} ({message.author.id})]: "{response}"\n'
            with open('messages.log', 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except discord.Forbidden:
            print(f"Kann DM nicht an {message.author} senden (blockiert).")
        except Exception as e:
            print(f"Fehler bei DM-Antwort an {message.author}: {e}")

    await bot.process_commands(message)

# ---------- AI Befehle ----------
@bot.hybrid_command(name="ask", description="Frage die KI (Text oder Bild)")
@app_commands.choices(model=[
    app_commands.Choice(name="▬▬DeepSeek▬▬", value=""),
    app_commands.Choice(name="DeepSeek Chat", value="deepseek-chat"),
    app_commands.Choice(name="DeepSeek DeepThink", value="deepseek-reasoner"),
    app_commands.Choice(name="▬▬ChatGPT▬▬", value=""),
    app_commands.Choice(name="GPT-5", value="gpt-5.1"),
    app_commands.Choice(name="GPT-4", value="gpt-4o"),
    app_commands.Choice(name="▬▬Claude▬▬", value=""),
    app_commands.Choice(name="Claude Opus", value="claude-opus-4-5-latest"),
    app_commands.Choice(name="Claude Haiku", value="claude-haiku-4.5"),
    app_commands.Choice(name="Claude Sonnet", value="claude-sonnet-4.5"),
    app_commands.Choice(name="▬▬Grok▬▬", value=""),
    app_commands.Choice(name="Grok 3", value="grok-3"),
    app_commands.Choice(name="Grok Fast", value="grok-3-fast"),
    app_commands.Choice(name="Grok Mini", value="grok-3-mini"),
    app_commands.Choice(name="Grok Mini Fast", value="grok-3-mini-fast"),
    app_commands.Choice(name="▬▬Gemini▬▬", value=""),
    app_commands.Choice(name="Gemini Flash", value="gemini-2.5-flash"),
    app_commands.Choice(name="Gemini Flash Lite", value="gemini-2.5-flash-lite"),
    app_commands.Choice(name="Gemini Pro", value="gemini-2.5-pro"),
    app_commands.Choice(name="▬▬Qwen▬▬", value=""),
    app_commands.Choice(name="Qwen thinking", value="openrouter:qwen/qwen3-vl-8b-thinking"),
    app_commands.Choice(name="Qwen instruct", value="openrouter:qwen/qwen3-vl-8b-instruct"),
])
async def ask(ctx, user_prompt: str, model: app_commands.Choice[str] = None):
    model_value = model.value if model else None
    await ask_prompt(ctx, prompt=user_prompt, model=model_value)

async def ask_prompt(ctx, *, prompt: str, model: str = None):
    if ctx.interaction:
        await ctx.defer()
        # Logging simulieren
        class FakeMessage:
            def __init__(self, content, author, guild, channel):
                self.content = content
                self.author = author
                self.guild = guild
                self.channel = channel
        fake_msg = FakeMessage(f"/ask {prompt}", ctx.author, ctx.guild, ctx.channel)
        log_message(fake_msg)
    else:
        log_message(ctx.message)

    response = await deepseek(prompt, model)

    if len(response) > 2000:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"response_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response)
        await ctx.send("Antwort zu lang – hier als Datei:", file=discord.File(filename))
        os.remove(filename)
    else:
        embed = discord.Embed(title="KI-Antwort", description=response, color=0x00ff00)
        if model:
            embed.set_footer(text=f"Modell: {model}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

@bot.hybrid_command(name="senddm", description="Sende eine DM an einen Benutzer (Admin)")
@app_commands.describe(user="Benutzer (ID, @mention, oder name#1234)", message="Nachricht")
async def send_dm(ctx, user: str, *, message: str):
    if ctx.interaction:
        await ctx.defer(ephemeral=True)
        # Logging
        class FakeMessage:
            def __init__(self, content, author, guild, channel):
                self.content = content
                self.author = author
                self.guild = guild
                self.channel = channel
        fake_msg = FakeMessage(f"/senddm {user} {message}", ctx.author, ctx.guild, ctx.channel)
        log_message(fake_msg)
    else:
        log_message(ctx.message)

    if not ctx.author.guild_permissions.administrator and ctx.author.id != bot.owner_id:
        await ctx.send("❌ Keine Berechtigung.", ephemeral=True)
        return

    target_user = None
    try:
        if user.startswith('<@') and user.endswith('>'):
            uid = user.strip('<@!>')
            target_user = await bot.fetch_user(int(uid))
        elif user.isdigit():
            target_user = bot.get_user(int(user)) or await bot.fetch_user(int(user))
        elif '#' in user:
            name, disc = user.split('#', 1)
            for guild in bot.guilds:
                member = discord.utils.get(guild.members, name=name, discriminator=disc)
                if member:
                    target_user = member
                    break
        else:
            if ctx.guild:
                member = discord.utils.get(ctx.guild.members, name=user)
                if member:
                    target_user = member
            if not target_user:
                for guild in bot.guilds:
                    member = discord.utils.get(guild.members, name=user)
                    if member:
                        target_user = member
                        break
        if not target_user:
            await ctx.send("❌ Benutzer nicht gefunden.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Nachricht von {ctx.author}", description=message, color=0x3498db)
        await target_user.send(embed=embed)
        await ctx.send(f"✅ DM an {target_user.mention} gesendet.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}", ephemeral=True)

@bot.command(name="reply")
async def reply_cmd(ctx, *, msg):
    log_message(ctx.message)
    response = await deepseek(msg, model=None)
    await ctx.reply(response)

# ---------- Cogs laden ----------
async def load_ha_cogs():
    cogs = [
        "cogs.welcome",
        "cogs.tiktok_live",
        "cogs.leveling",
        "cogs.minigames",
        "cogs.beauty_tips"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog geladen: {cog}")
        except Exception as e:
            print(f"❌ Fehler beim Laden von {cog}: {e}")

# ---------- Start ----------
async def main():
    async with bot:
        await load_ha_cogs()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())