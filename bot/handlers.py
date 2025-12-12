from typing import Optional

import requests
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.db import get_user_token, save_user_token
from bot.yandex_client import get_disk_info, upload_file_to_yandex
import os

router = Router()

YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"


def register_handlers(dp):
    dp.include_router(router)


# 👋 /start
@router.message(CommandStart())
async def start_cmd(message: Message):
    text = (
        "👋 Привет! Я — CloudBridge Bot.\n\n"
        "Я сохраняю любые файлы, фото и видео, которые ты мне отправишь, "
        "на твой Яндекс.Диск 📁.\n\n"
        "📦 Что я умею:\n"
        "• сохранять фото, документы, видео, голосовые и даже стикеры;\n"
        "• показывать, сколько места осталось на диске;\n"
        "• автоматически создавать нужные папки.\n\n"
        "Отправь мне любой файл, и я сразу сохраню его на диск!"
    )
    await message.answer(text)


# 🔗 /connect
@router.message(Command("connect"))
async def connect_cmd(message: Message):
    client_id = os.getenv("YANDEX_CLIENT_ID")

    if not client_id:
        await message.answer("⚠️ Client ID Яндекс.Диска не настроен. Обратитесь к администратору.")
        return

    params = [
        "response_type=code",
        f"client_id={client_id}",
        f"state={message.from_user.id}",
    ]
    link = f"{YANDEX_AUTH_URL}?" + "&".join(params)

    await message.answer(
        "🔗 Подключаем Яндекс.Диск вручную:\n\n"
        "1. Нажми на ссылку ниже и войди в аккаунт Яндекс.\n"
        "2. Нажми \"Разрешить\" — откроется страница с кодом подтверждения.\n"
        "3. Скопируй код (verification_code) и отправь его мне одним сообщением.\n\n"
        f"Ссылка: {link}\n\n"
        "Я жду код здесь и подключу диск сразу после того, как ты его пришлёшь.",
    )


# Принятие authorization_code
@router.message(F.text.regexp(r"^[A-Za-z0-9\-_]{20,}$"))
async def handle_auth_code(message: Message):
    code = message.text.strip()
    token = exchange_code_for_token(code)

    if not token:
        await message.answer("❌ Не удалось обменять код на токен. Попробуй ещё раз или проверь настройки.")
        return

    save_user_token(message.from_user.id, token)
    await message.answer("✅ Успешно подключено! Теперь я буду сохранять файлы в твой Яндекс.Диск ☁️")


# ----------------------- Обработчики типов -----------------------

@router.message(F.document)
async def handle_document(message: Message):
    await process_file(message, file_type="document")


@router.message(F.photo)
async def handle_photo(message: Message):
    await process_file(message, file_type="photo")


@router.message(F.video)
async def handle_video(message: Message):
    await process_file(message, file_type="video")


@router.message(F.voice)
async def handle_voice(message: Message):
    await process_file(message, file_type="voice")


@router.message(F.sticker)
async def handle_sticker(message: Message):
    await process_file(message, file_type="sticker")


# ----------------------- Вспомогательная логика -----------------------

def exchange_code_for_token(code: str) -> Optional[str]:
    client_id = os.getenv("YANDEX_CLIENT_ID")
    client_secret = os.getenv("YANDEX_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    resp = requests.post(YANDEX_TOKEN_URL, data=data)
    if resp.status_code != 200:
        return None

    return resp.json().get("access_token")


async def process_file(message: Message, file_type: str):
    bot = message.bot
    file_name = ""

    token = get_user_token(message.from_user.id)
    if not token:
        await message.reply("⚠️ Сначала подключи Яндекс.Диск через /connect.")
        return

    # Определяем тип файла и имя
    if file_type == "document":
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif file_type == "photo":
        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id}.jpg"
    elif file_type == "video":
        file_id = message.video.file_id
        file_name = f"video_{file_id}.mp4"
    elif file_type == "voice":
        file_id = message.voice.file_id
        file_name = f"voice_{file_id}.ogg"
    elif file_type == "sticker":
        file_id = message.sticker.file_id
        file_name = f"sticker_{file_id}.webp"
    else:
        await message.reply("⚠️ Этот тип файла пока не поддерживается.")
        return

    # Скачиваем файл
    file = await bot.get_file(file_id)
    file_path = file.file_path
    local_path = f"tmp_{file_name}"
    await bot.download_file(file_path, local_path)

    # Загружаем на диск
    success = upload_file_to_yandex(local_path, f"TelegramUploads/{file_name}", token)

    # Удаляем временный файл
    if os.path.exists(local_path):
        os.remove(local_path)

    # Ответ пользователю
    if success:
        info = get_disk_info(token)
        free_space_gb = info["free_space"] / 1024**3
        used_space_gb = info["used_space"] / 1024**3
        total_space_gb = info["total_space"] / 1024**3

        await message.reply(
            f"✅ Файл успешно загружен!\n\n"
            f"💾 Использовано: {used_space_gb:.2f} ГБ / {total_space_gb:.2f} ГБ\n"
            f"🧭 Свободно: {free_space_gb:.2f} ГБ\n"
            f"📥 Лимит загрузок на сегодня: не ограничен"
        )
    else:
        await message.reply("❌ Ошибка при загрузке файла.")
