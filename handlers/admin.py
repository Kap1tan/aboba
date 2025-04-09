import os
import tempfile
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from config import ADMIN_IDS, GIFT_EMOJIS, GIFT_NAMES
from keyboards import (
    create_admin_keyboard,
    create_back_to_admin_keyboard
)
from utils import is_admin, load_json_data, save_json_data

admin_router = Router()

def get_global_roulette_stats(roulette_stats):
    """Собирает общую статистику рулетки"""
    total_spins = 0
    total_spent = 0
    total_won = 0
    total_gifts = {}

    for user_id, stats in roulette_stats.items():
        total_spins += stats.get("total_spins", 0)
        total_spent += stats.get("total_spent", 0)
        total_won += stats.get("total_won", 0)

        # Суммируем подарки
        for gift, count in stats.get("gifts", {}).items():
            if gift not in total_gifts:
                total_gifts[gift] = 0
            total_gifts[gift] += count

    # Формируем список всех подарков
    gifts_text = ""
    for gift, count in sorted(total_gifts.items(), key=lambda x: x[1], reverse=True):
        emoji = GIFT_EMOJIS.get(gift, "🎁")
        name = GIFT_NAMES.get(gift, "Подарок")
        gifts_text += f"{emoji} {name}: {count} шт.\n"

    # Вычисляем прибыль/убыток платформы
    profit = total_spent - total_won
    profit_percentage = (profit / total_spent * 100) if total_spent > 0 else 0

    stats_text = (
        f"📊 Общая статистика рулетки:\n\n"
        f"Всего прокрутов: {total_spins}\n"
        f"Получено звезд: {total_spent}\n"
        f"Выдано подарков на: {total_won} звезд\n"
        f"Прибыль: {profit} звезд ({profit_percentage:.2f}%)\n\n"
        f"Выданные подарки:\n{gifts_text}"
    )

    return stats_text

@admin_router.message(Command(commands="admin"))
async def cmd_admin(message: Message):
    """Admin panel command handler."""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return

    # Получаем пользовательские данные из initial_data
    users_data = message.bot.initial_data['users_data']

    total_users = len(users_data)
    active_users = sum(1 for u in users_data.values() if u.get("status") == "active")
    removed_users = sum(1 for u in users_data.values() if u.get("status") == "removed")

    admin_text = (
        "📊 <b>Админ панель</b>:\n\n"
        f"Всего пользователей: <b>{total_users}</b>\n"
        f"Активных пользователей: <b>{active_users}</b>\n"
        f"Удалили бота: <b>{removed_users}</b>\n\n"
        "Выберите действие:"
    )

    await message.answer(
        admin_text,
        reply_markup=create_admin_keyboard(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "roulette_stats")
async def callback_roulette_stats(callback: CallbackQuery):
    """Показать статистику рулетки для админа"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    # Получаем статистику рулетки из initial_data
    roulette_stats = callback.bot.initial_data['roulette_stats']

    # Собираем общую статистику
    stats_text = get_global_roulette_stats(roulette_stats)

    await callback.message.edit_text(
        stats_text,
        reply_markup=create_back_to_admin_keyboard()
    )
    await callback.answer()

@admin_router.callback_query(F.data == "back_to_admin")
async def callback_back_to_admin(callback: CallbackQuery):
    """Вернуться в админ-панель"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    await cmd_admin(callback.message)
    await callback.answer()

@admin_router.callback_query(F.data == "download_users")
async def callback_download_users(callback: CallbackQuery):
    """Download users data as a file."""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    # Получаем пользовательские данные из initial_data
    users_data = callback.bot.initial_data['users_data']

    lines = []
    for user_id, info in users_data.items():
        username = info.get("username", "Неизвестно")
        status = info.get("status", "unknown")
        joined_at = info.get("joined_at", "Неизвестно")
        line = f"Имя: {username}, Статус: {status}, ID: {user_id}, Дата: {joined_at}"
        lines.append(line)

    text_content = "\n".join(lines) if lines else "Список пользователей пуст."

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(text_content)
        tmp_path = tmp.name

    document = FSInputFile(tmp_path)
    await callback.bot.send_document(
        chat_id=callback.from_user.id,
        document=document,
        caption="Список всех пользователей"
    )

    os.remove(tmp_path)
    await callback.answer()