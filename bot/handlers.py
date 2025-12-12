from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from bot.yandex_client import upload_file_to_yandex

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.message(F.document)
async def handle_file(message: Message):
    file = await message.bot.get_file(message.document.file_id)
    file_path = file.file_path
    file_name = message.document.file_name

    # Скачиваем временно файл
    file_on_disk = f"/tmp/{file_name}"
    await message.bot.download_file(file_path, file_on_disk)

    # Отправляем на Яндекс.Диск
    success = upload_file_to_yandex(file_on_disk, f"TelegramUploads/{file_name}")

    if success:
        await message.reply("✅ Файл успешно загружен на Яндекс.Диск!")
    else:
        await message.reply("❌ Ошибка при загрузке файла.")
