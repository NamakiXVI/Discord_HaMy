import discord
from discord.ext import commands
from discord import app_commands

from config import WELCOME_CHANNEL_ID, MEMBER_ROLE_ID, COLOR_PRIMARY


class Welcome(commands.Cog):
    """Automatische Rollenzuweisung und Willkommensnachrichten."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Wird ausgelöst, wenn ein Mitglied dem Server beitritt."""
        # Auto-Role zuweisen
        if MEMBER_ROLE_ID:
            role = member.guild.get_role(MEMBER_ROLE_ID)
            if role:
                try:
                    await member.add_roles(role, reason="Automatische Rollenzuweisung")
                except discord.Forbidden:
                    pass  # Bot hat keine Berechtigung

        # Willkommensnachricht senden
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🌸 Willkommen in Ha Mys Ausbeutungsbunker! 🌸",
            description=(
                f"Hey {member.mention}, herzlich willkommen auf dem Server!\n\n"
                f"**Über Ha My:**\n"
                f"**Wichtige Links:**\n"
                f"🎥 [Ha My TikTok](https://tiktok.com/@ha.my07_)\n"
                f"📢 <#{LIVE_NOTIFICATION_CHANNEL_ID}> — Live-Benachrichtigungen\n"
                f"💬 Allgemeiner Chat"
                f""
            ),
            color=COLOR_PRIMARY
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Mitglied #{len(member.guild.members)}")

        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))