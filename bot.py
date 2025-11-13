import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)


# ------------------------------------
# IA: DeepSeek (versión de pago)
# ------------------------------------
async def deepseek_generate(prompt: str) -> str:
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",   # 🔥 MODELO RECOMENDADO Y BARATO
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()

            # Si DeepSeek devuelve un error, lo mostramos en Discord
            if "choices" not in data:
                return f"⚠️ Error en la API DeepSeek:\n```json\n{data}\n```"

            try:
                return data["choices"][0]["message"]["content"]
            except:
                return f"⚠️ Respuesta inesperada de DeepSeek:\n```json\n{data}\n```"


# ---------------------------
# Evento ON_READY
# ---------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BOT EN LÍNEA como {bot.user}")


# ---------------------------
# Comando /ask
# ---------------------------
@bot.tree.command(name="ask", description="Hazle una pregunta al bot.")
async def ask(interaction: discord.Interaction, pregunta: str):
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(pregunta)
    await interaction.followup.send(respuesta)


# ---------------------------
# Comando /attack
# ---------------------------
@bot.tree.command(name="attack", description="Realiza un ataque narrado.")
async def attack(interaction: discord.Interaction, accion: str):
    prompt = f"Describe un ataque de rol: {accion}. Sé narrativo, detallado y épico."
    await interaction.response.defer(thinking=True)
    respuesta = await deepseek_generate(prompt)
    await interaction.followup.send(respuesta)


# ---------------------------
# Iniciar bot
# ---------------------------
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
