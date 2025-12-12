from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from bot.yandex_client import upload_file_to_yandex, get_disk_info
import os

router = Router()

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

async def process_file(message: Message, file_type: str):
    bot = message.bot
    file_name = ""

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
    success = upload_file_to_yandex(local_path, f"TelegramUploads/{file_name}")

    # Удаляем временный файл
    if os.path.exists(local_path):
        os.remove(local_path)

    # Ответ пользователю
    if success:
        info = get_disk_info()
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
