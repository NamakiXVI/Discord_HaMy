import random
import discord
from discord.ext import commands
from discord import app_commands

from utils.database import Database
from config import XP_PER_MESSAGE, XP_PER_LEVEL, COLOR_PRIMARY

db = Database("data/bot.db")


class Leveling(commands.Cog):
    """Level-System zur Förderung der Community-Aktivität."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = db
        self._init_database()

    def _init_database(self):
        """Initialisiert die Datenbank-Tabelle."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS user_xp (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        """)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Vergibt XP für Nachrichten."""
        if message.author.bot:
            return
        if not message.guild:
            return

        # Zufällige XP vergeben
        xp_gained = random.randint(*XP_PER_MESSAGE)
        user_id = message.author.id

        # Aktuelle XP abrufen
        result = self.db.fetch_one(
            "SELECT xp, level FROM user_xp WHERE user_id = ?",
            (user_id,)
        )

        if result:
            current_xp, current_level = result
        else:
            current_xp, current_level = 0, 1
            self.db.execute(
                "INSERT INTO user_xp (user_id, xp, level) VALUES (?, ?, ?)",
                (user_id, 0, 1)
            )

        new_xp = current_xp + xp_gained
        new_level = current_level

        # Level-Up prüfen
        while new_xp >= new_level * XP_PER_LEVEL:
            new_xp -= new_level * XP_PER_LEVEL
            new_level += 1

            # Level-Up Nachricht senden
            if new_level > current_level:
                embed = discord.Embed(
                    title="🎉 Level Up! 🎉",
                    description=(
                        f"{message.author.mention} ist auf **Level {new_level}** "
                        f"aufgestiegen!"
                    ),
                    color=COLOR_PRIMARY
                )
                await message.channel.send(embed=embed)

        # Datenbank aktualisieren
        self.db.execute(
            "UPDATE user_xp SET xp = ?, level = ? WHERE user_id = ?",
            (new_xp, new_level, user_id)
        )

    @app_commands.command(name="rank", description="Zeigt dein aktuelles Level und XP-Fortschritt.")
    @app_commands.describe(user="Optional: Zeige den Rank eines anderen Mitglieds")
    async def rank(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None
    ):
        """Zeigt Level und XP-Fortschritt an."""
        target = user or interaction.user

        result = self.db.fetch_one(
            "SELECT xp, level FROM user_xp WHERE user_id = ?",
            (target.id,)
        )

        if not result:
            xp, level = 0, 1
        else:
            xp, level = result

        xp_needed = level * XP_PER_LEVEL
        progress = int((xp / xp_needed) * 20) if xp_needed > 0 else 0

        progress_bar = "█" * progress + "░" * (20 - progress)

        embed = discord.Embed(
            title=f"🏆 Rank von {target.display_name}",
            color=COLOR_PRIMARY
        )
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}** / {xp_needed}", inline=True)
        embed.add_field(
            name="Fortschritt",
            value=f"`{progress_bar}` ({int((xp / xp_needed) * 100) if xp_needed > 0 else 0}%)",
            inline=False
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Zeigt die Top 10 der aktivsten Mitglieder.")
    async def leaderboard(self, interaction: discord.Interaction):
        """Zeigt die XP-Bestenliste an."""
        results = self.db.fetch_all(
            "SELECT user_id, level, xp FROM user_xp ORDER BY level DESC, xp DESC LIMIT 10"
        )

        if not results:
            await interaction.response.send_message(
                "Noch keine Einträge im Leaderboard!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏅 Ha My's Community Leaderboard 🏅",
            color=COLOR_PRIMARY
        )

        description = ""
        medals = ["🥇", "🥈", "🥉"]

        for i, (user_id, level, xp) in enumerate(results):
            user = interaction.guild.get_member(user_id)
            name = user.display_name if user else f"User {user_id}"

            medal = medals[i] if i < 3 else f"{i+1}."
            description += f"{medal} **{name}** — Level {level} ({xp} XP)\n"

        embed.description = description
        embed.set_footer(text="Schreibe Nachrichten, um XP zu sammeln!")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))