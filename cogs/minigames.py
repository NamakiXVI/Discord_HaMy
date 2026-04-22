import random
import discord
from discord.ext import commands
from discord import app_commands

from config import COLOR_PRIMARY


class Minigames(commands.Cog):
    """Mini-Spiele für die Community."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rps", description="Schere, Stein, Papier gegen den Bot!")
    @app_commands.describe(wahl="Deine Wahl")
    @app_commands.choices(wahl=[
        app_commands.Choice(name="🪨 Stein", value="stein"),
        app_commands.Choice(name="📄 Papier", value="papier"),
        app_commands.Choice(name="✂️ Schere", value="schere")
    ])
    async def rps(self, interaction: discord.Interaction, wahl: str):
        """Schere, Stein, Papier Spiel."""
        choices = ["stein", "papier", "schere"]
        bot_choice = random.choice(choices)

        # Gewinner bestimmen
        if wahl == bot_choice:
            result = "Unentschieden!"
            emoji = "🤝"
        elif (wahl == "stein" and bot_choice == "schere") or \
             (wahl == "papier" and bot_choice == "stein") or \
             (wahl == "schere" and bot_choice == "papier"):
            result = f"{interaction.user.mention} gewinnt! 🎉"
            emoji = "🏆"
        else:
            result = "Der Bot gewinnt! 🤖"
            emoji = "😢"

        choice_emojis = {"stein": "🪨", "papier": "📄", "schere": "✂️"}

        embed = discord.Embed(
            title=f"{emoji} Schere, Stein, Papier {emoji}",
            color=COLOR_PRIMARY
        )
        embed.add_field(
            name=f"{interaction.user.display_name}",
            value=choice_emojis[wahl],
            inline=True
        )
        embed.add_field(
            name="Bot",
            value=choice_emojis[bot_choice],
            inline=True
        )
        embed.add_field(name="Ergebnis", value=result, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="würfel", description="Wirf einen Würfel!")
    @app_commands.describe(seiten="Anzahl der Seiten (Standard: 6)")
    async def dice(self, interaction: discord.Interaction, seiten: int = 6):
        """Wirft einen Würfel mit konfigurierbarer Seitenzahl."""
        if seiten < 2:
            await interaction.response.send_message(
                "❌ Ein Würfel muss mindestens 2 Seiten haben!",
                ephemeral=True
            )
            return

        result = random.randint(1, seiten)

        embed = discord.Embed(
            title="🎲 Würfelwurf",
            description=f"{interaction.user.mention} hat eine **{result}** gewürfelt!",
            color=COLOR_PRIMARY
        )
        embed.set_footer(text=f"W{seiten}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="münze", description="Wirf eine Münze!")
    async def coinflip(self, interaction: discord.Interaction):
        """Wirft eine Münze (Kopf oder Zahl)."""
        result = random.choice(["Kopf", "Zahl"])
        emoji = "🪙" if result == "Kopf" else "💿"

        embed = discord.Embed(
            title=f"{emoji} Münzwurf",
            description=f"{interaction.user.mention} hat **{result}** geworfen!",
            color=COLOR_PRIMARY
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Minigames(bot))