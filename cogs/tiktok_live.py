import asyncio
import logging
import discord
from discord.ext import commands, tasks
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent

from config import (
    TIKTOK_USERNAME, LIVE_NOTIFICATION_CHANNEL_ID,
    COLOR_TIKTOK, COLOR_PRIMARY
)

logger = logging.getLogger("HaMyBot.TikTokLive")


class TikTokLiveNotifications(commands.Cog):
    """Benachrichtigt die Community, wenn Ha My auf TikTok live geht."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client: TikTokLiveClient = None
        self.is_live = False
        self.monitor_loop.start()

    def cog_unload(self):
        """Cleanup beim Entladen des Cogs."""
        self.monitor_loop.cancel()

    async def send_live_notification(self):
        """Sendet eine Live-Benachrichtigung in den konfigurierten Kanal."""
        channel = self.bot.get_channel(LIVE_NOTIFICATION_CHANNEL_ID)
        if not channel:
            logger.warning("Live-Benachrichtigungskanal nicht gefunden!")
            return

        embed = discord.Embed(
            title="🔴 HA MY IST JETZT LIVE AUF TIKTOK! 🔴",
            description=(
                f"**[Jetzt zuschauen!](https://tiktok.com/@{TIKTOK_USERNAME}/live)**\n\n"
                f"Ha My streamt gerade — schau vorbei und unterstütze sie! "
                f"Lass ein paar Likes und Kommentare da. 💖"
            ),
            color=COLOR_TIKTOK
        )
        embed.set_thumbnail(url="https://img.icons8.com/color/48/tiktok--v1.png")
        embed.set_footer(text=f"TikTok Live • @{TIKTOK_USERNAME}")

        await channel.send(content="@everyone Ha My ist live!", embed=embed)
        logger.info("Live-Benachrichtigung gesendet.")

    @tasks.loop(minutes=1)
    async def monitor_loop(self):
        """Überprüft regelmäßig, ob Ha My live ist."""
        try:
            # Kurzer Verbindungstest — TikTokLiveClient verbindet sich nur,
            # wenn der Stream tatsächlich live ist
            client = TikTokLiveClient(unique_id=f"@{TIKTOK_USERNAME}")

            connected = False

            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                nonlocal connected
                connected = True
                if not self.is_live:
                    self.is_live = True
                    await self.send_live_notification()
                await client.disconnect()

            @client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                pass

            try:
                # Timeout nach 10 Sekunden, falls keine Verbindung zustande kommt
                await asyncio.wait_for(client.start(), timeout=10.0)
            except asyncio.TimeoutError:
                # Kein Live-Stream — normal
                if self.is_live:
                    self.is_live = False
                    logger.info("Ha My ist nicht mehr live.")
            except Exception as e:
                logger.error(f"Fehler bei TikTok-Verbindung: {e}")

        except Exception as e:
            logger.error(f"Fehler im Monitor-Loop: {e}")

    @monitor_loop.before_loop
    async def before_monitor(self):
        """Wartet, bis der Bot bereit ist."""
        await self.bot.wait_until_ready()
        logger.info("TikTok Live Monitor gestartet.")


async def setup(bot: commands.Bot):
    await bot.add_cog(TikTokLiveNotifications(bot))