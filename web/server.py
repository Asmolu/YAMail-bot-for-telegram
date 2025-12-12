import os
from typing import Optional

from aiogram import Bot
from fastapi import FastAPI, HTTPException

from bot.db import save_user_token
from bot.handlers import exchange_code_for_token

app = FastAPI()
_telegram_bot: Optional[Bot] = None


def setup_bot(bot: Bot) -> None:
    global _telegram_bot
    _telegram_bot = bot

@app.get("/health")
async def healthcheck():
    return {"status": "ok"}


@app.get("/oauth/callback")
async def oauth_callback(code: str, state: Optional[str] = None):
    if state is None:
        raise HTTPException(status_code=400, detail="Missing state with Telegram user id")

    token = exchange_code_for_token(code)
    if not token:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    save_user_token(user_id, token)

    if _telegram_bot:
        await _telegram_bot.send_message(
            chat_id=user_id,
            text="✅ Я подключил твой Яндекс.Диск! Теперь можешь отправлять файлы, и я сохраню их автоматически.",
        )

    host = os.getenv("PUBLIC_APP_HOST", "")
    return {
        "status": "ok",
        "message": "Yandex Disk connected",
        "next_step": "Вернись в чат с ботом и отправь файл",
        "bot_chat": host,
    }