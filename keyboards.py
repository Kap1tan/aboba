from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_keyboard(subscribed: bool):
    """Создаем стартовую клавиатуру"""
    if subscribed:
        # Пользователь уже подписан, не показываем кнопку подписки
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎮 Играть", callback_data="play_game")]
            ]
        )
    else:
        # Пользователь не подписан, показываем обе кнопки
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎮 Играть", callback_data="play_game")],
                [InlineKeyboardButton(
                    text="📢 Подписаться |+15% к удаче",
                    url="https://t.me/GiftsForFree_News"
                )]
            ]
        )

    return keyboard


def get_bet_keyboard():
    """Создаем клавиатуру для выбора ставки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="25 ⭐", callback_data="bet_25")],
            [InlineKeyboardButton(text="50 ⭐", callback_data="bet_50")],
            [InlineKeyboardButton(text="100 ⭐", callback_data="bet_100")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start")]
        ]
    )
    return keyboard


def get_payment_keyboard(amount):
    """Создаем клавиатуру для оплаты"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить {amount} ⭐", pay=True)
    builder.button(text="🔙 Отмена", callback_data="back_to_bet")
    return builder.as_markup()


def create_admin_keyboard():
    """Создаем клавиатуру для admin панели"""
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Скачать всех юзеров", callback_data="download_users")],
        [InlineKeyboardButton(text="💬 Создать рассылку", callback_data="create_broadcast")],
        [InlineKeyboardButton(text="📊 Статистика рулетки", callback_data="roulette_stats")]
    ])
    return inline_kb


def create_back_to_admin_keyboard():
    """Создаем кнопку возврата в admin панель"""
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
    ])
    return back_kb