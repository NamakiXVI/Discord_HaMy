import asyncio
import logging
import discord
from discord.ext import commands

from config import BOT_TOKEN, GUILD_ID

# === Logging konfigurieren ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HaMyBot")


class HaMyBot(commands.Bot):
    """Hauptklasse für Ha Mys Discord Bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True           # Für on_member_join
        intents.message_content = True   # Für Befehlsverarbeitung

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None  # Wir erstellen einen eigenen Help-Command
        )

    async def setup_hook(self):
        """Wird beim Start des Bots ausgeführt."""
        # Alle Cogs laden
        cogs_to_load = [
            "cogs.welcome",
            "cogs.tiktok_live",
            "cogs.tiktok_stats",
            "cogs.beauty_tips",
            "cogs.polls",
            "cogs.giveaways",
            "cogs.leveling",
            "cogs.music_queue",
            "cogs.stream_schedule",
            "cogs.feedback",
            "cogs.notifications",
            "cogs.minigames"
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Cog geladen: {cog}")
            except Exception as e:
                logger.error(f"Fehler beim Laden von {cog}: {e}")

        # Slash Commands mit Discord synchronisieren
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Slash Commands für Guild {GUILD_ID} synchronisiert")
        else:
            await self.tree.sync()
            logger.info("Slash Commands global synchronisiert")

    async def on_ready(self):
        """Wird ausgeführt, wenn der Bot bereit ist."""
        logger.info(f"Bot eingeloggt als {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"@hamy042494 auf TikTok"
            )
        )
        logger.info("=== HaMy Discord Bot ist bereit! ===")


async def main():
    """Hauptfunktion zum Starten des Bots."""
    bot = HaMyBot()

    async with bot:
        await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())