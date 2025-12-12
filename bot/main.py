import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import uvicorn

from bot.db import init_db
from bot.handlers import register_handlers
from web.server import setup_bot

logging.basicConfig(level=logging.INFO)
load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()


async def main():
    init_db()
    register_handlers(dp)
    setup_bot(bot)

    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))

    server = uvicorn.Server(
        uvicorn.Config("bot.server:app", host=api_host, port=api_port, log_level="info")
    )

    await asyncio.gather(dp.start_polling(bot), server.serve())


if __name__ == "__main__":
    asyncio.run(main())
