import logging
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS
from keyboards import create_admin_keyboard
from utils import is_admin

broadcast_router = Router()

# Флаг для режима рассылки
broadcast_mode = False

@broadcast_router.callback_query(F.data == "create_broadcast")
async def callback_create_broadcast(callback: CallbackQuery):
    """Start broadcast mode."""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    global broadcast_mode
    broadcast_mode = True

    await callback.message.answer(
        "Отправьте сообщение, которое нужно разослать всем активным пользователям.\n\n"
        "<b>Поддерживаются:</b> \n"
        "- <b>Текст</b> (без форматирования)\n"
        "- <b>Фото</b> (С описанием, без форматирования)\n"
        "- <b>Видео</b> (С описанием, без форматирования)\n"
        "- <b>Документ</b> (С описанием, без форматирования)\n"
        "- <b>Аудио</b> (С описанием, без форматирования)\n"
        "- <b>Голосовое сообщение</b> (С описанием, без форматирования)\n"
        "- <b>Видеосообщение</b>",
        parse_mode="HTML"
    )

    await callback.answer()

@broadcast_router.message()
async def handle_broadcast(message: Message):
    """Handle broadcast messages."""
    global broadcast_mode

    # Проверяем, является ли пользователь администратором и активен ли режим рассылки
    if not is_admin(message.from_user.id) or not broadcast_mode:
        return

    # Получаем пользовательские данные из initial_data
    users_data = message.bot.initial_data['users_data']

    # Процесс рассылки
    count = 0
    errors = 0

    for user_id, info in users_data.items():
        if info.get("status") == "active":
            try:
                if message.photo:
                    photo_id = message.photo[-1].file_id
                    await message.bot.send_photo(
                        chat_id=int(user_id),
                        photo=photo_id,
                        caption=message.caption or ""
                    )
                elif message.video:
                    await message.bot.send_video(
                        chat_id=int(user_id),
                        video=message.video.file_id,
                        caption=message.caption or ""
                    )
                elif message.document:
                    await message.bot.send_document(
                        chat_id=int(user_id),
                        document=message.document.file_id,
                        caption=message.caption or ""
                    )
                elif message.audio:
                    await message.bot.send_audio(
                        chat_id=int(user_id),
                        audio=message.audio.file_id,
                        caption=message.caption or ""
                    )
                elif message.voice:
                    await message.bot.send_voice(
                        chat_id=int(user_id),
                        voice=message.voice.file_id,
                        caption=message.caption or ""
                    )
                elif message.video_note:
                    await message.bot.send_video_note(
                        chat_id=int(user_id),
                        video_note=message.video_note.file_id
                    )
                else:
                    await message.bot.send_message(
                        chat_id=int(user_id),
                        text=message.text
                    )

                count += 1
                # Добавляем небольшую задержку, чтобы избежать ограничений
                await asyncio.sleep(0.05)
            except Exception as e:
                logging.error(f"Error sending broadcast to user {user_id}: {e}")
                errors += 1

    # Отправляем отчет об успешной рассылке
    await message.answer(
        f"Рассылка отправлена {count} пользователям. Ошибок: {errors}."
    )

    # Деактивируем режим рассылки
    broadcast_mode = False