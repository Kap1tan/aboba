from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import get_start_keyboard, get_bet_keyboard
from utils import add_user, is_admin

start_router = Router()


async def is_subscribed(user_id: int, bot, chat_id: str = "@GiftsForFree_News"):
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False


@start_router.message(Command(commands="start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    display_name = username

    # Получаем пользовательские данные из initial_data
    users_data = message.bot.initial_data['users_data']

    # Добавляем пользователя в базу данных
    add_user(users_data, user_id, display_name)

    # Получаем клавиатуру в зависимости от подписки
    subscribed = await is_subscribed(user_id, message.bot)
    keyboard = get_start_keyboard(subscribed)

    await message.answer(
        "🎁 Испытайте удачу и получите редкий подарок за небольшую плату! 🍀",
        reply_markup=keyboard
    )


@start_router.callback_query(F.data == "play_game")
async def callback_play_game(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎲 Выберите ставку:",
        reply_markup=get_bet_keyboard()
    )
    await callback.answer()


@start_router.callback_query(F.data == "back_to_start")
async def callback_back_to_start(callback: CallbackQuery):
    # Получаем клавиатуру в зависимости от подписки
    subscribed = await is_subscribed(callback.from_user.id, callback.bot)
    keyboard = get_start_keyboard(subscribed)

    await callback.message.edit_text(
        "🎁 Испытайте удачу и получите редкий подарок за небольшую плату! 🍀",
        reply_markup=keyboard
    )
    await callback.answer()