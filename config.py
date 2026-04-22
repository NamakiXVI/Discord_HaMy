import os
from dotenv import load_dotenv

load_dotenv()

# === Bot-Konfiguration ===
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = "!"  # Fallback-Präfix, hauptsächlich werden Slash-Commands genutzt

# === TikTok-Konfiguration ===
TIKTOK_USERNAME = "hamy042494"  # Ha Mys TikTok-Benutzername ohne @

# === Discord IDs ===
GUILD_ID = int(os.getenv("GUILD_ID", "0"))  # Server-ID für syncing
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
LIVE_NOTIFICATION_CHANNEL_ID = int(os.getenv("LIVE_NOTIFICATION_CHANNEL_ID", "0"))
ANNOUNCEMENT_CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID", "0"))

# === Rollen ===
MEMBER_ROLE_ID = int(os.getenv("MEMBER_ROLE_ID", "0"))

# === Farben für Embeds ===
COLOR_PRIMARY = 0xFF69B4    # Hot Pink — Ha Mys Beauty-Theme
COLOR_SUCCESS = 0x00FF00    # Grün
COLOR_ERROR = 0xFF0000      # Rot
COLOR_INFO = 0x3498DB       # Blau
COLOR_TIKTOK = 0x010101     # TikTok-Schwarz

# === Leveling-System ===
XP_PER_MESSAGE = (5, 15)    # Zufällige XP pro Nachricht
XP_PER_LEVEL = 100          # XP pro Level

# === Stream-Erinnerung ===
REMINDER_MINUTES_BEFORE = 30  # Erinnerung X Minuten vor Stream