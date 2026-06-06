from __future__ import annotations

import os

import discord
from dotenv import load_dotenv
from pathlib import Path

from app.openclaw_adapter import answer_from_openclaw


load_dotenv(dotenv_path=Path.cwd() / ".env", override=True)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "!rag")
EVAL_COMMAND_PREFIX = os.getenv("DISCORD_EVAL_COMMAND_PREFIX", "!rageval")
DEFAULT_DOCUMENT_ID = os.getenv("DISCORD_DEFAULT_DOCUMENT_ID")
DEFAULT_LIMIT = int(os.getenv("DISCORD_DEFAULT_LIMIT", "3"))
DEFAULT_MODEL = os.getenv("DISCORD_DEFAULT_MODEL", "gemma4:e4b")

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("Falta DISCORD_BOT_TOKEN en el archivo .env.")


def get_default_document_id() -> int | None:
    if DEFAULT_DOCUMENT_ID is None or DEFAULT_DOCUMENT_ID.strip() == "":
        return None

    return int(DEFAULT_DOCUMENT_ID)



def build_compact_answer(answer: str, query_id: int | None) -> str:
    """
    Construye una respuesta corta para Discord.
    Conserva la respuesta generada, pero elimina la ficha completa de evaluación.
    """
    main_answer = answer.split("\n---\n\nFicha para evaluación")[0].strip()

    return (
        f"query_id: {query_id}\n\n"
        f"{main_answer}\n\n"
        "Para ver la ficha completa de evaluación usá `!rageval` con la misma pregunta."
    )

def split_discord_message(text: str, max_length: int = 1900) -> list[str]:
    """
    Divide respuestas largas para evitar el límite de mensajes de Discord.
    Se usa 1900 para dejar margen bajo el límite de 2000 caracteres.
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    current = ""

    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > max_length:
            if current:
                parts.append(current)
                current = ""

            while len(line) > max_length:
                parts.append(line[:max_length])
                line = line[max_length:]

        current += line

    if current:
        parts.append(current)

    return parts


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    print(f"Bot conectado como {client.user}")
    print(f"Comando compacto activo: {COMMAND_PREFIX} <pregunta>")
    print(f"Comando evaluación activo: {EVAL_COMMAND_PREFIX} <pregunta>")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    content = message.content.strip()

    is_eval_mode = content.startswith(EVAL_COMMAND_PREFIX)
    is_compact_mode = content.startswith(COMMAND_PREFIX)

    if not is_eval_mode and not is_compact_mode:
        return

    if is_eval_mode:
        question = content[len(EVAL_COMMAND_PREFIX):].strip()
    else:
        question = content[len(COMMAND_PREFIX):].strip()

    if not question:
        await message.reply(
            f"Escribí una pregunta después de `{COMMAND_PREFIX}`. "
            f"Ejemplo: `{COMMAND_PREFIX} ¿Cuál es el objetivo principal de Kali Linux?` o `{EVAL_COMMAND_PREFIX} ¿Cuál es el objetivo principal de Kali Linux?`",
            mention_author=False,
        )
        return

    async with message.channel.typing():
        try:
            response = answer_from_openclaw(
                question=question,
                limit=DEFAULT_LIMIT,
                document_id=get_default_document_id(),
                channel="discord-direct",
                model=DEFAULT_MODEL,
            )

            if is_eval_mode:
                final_text = f"query_id: {response.query_id}\n\n" + response.answer
            else:
                final_text = build_compact_answer(
                    answer=response.answer,
                    query_id=response.query_id,
                )

            for part in split_discord_message(final_text):
                await message.reply(part, mention_author=False)

        except Exception as exc:
            await message.reply(
                f"Ocurrió un error al consultar el RAG: `{type(exc).__name__}: {exc}`",
                mention_author=False,
            )


client.run(DISCORD_BOT_TOKEN)
