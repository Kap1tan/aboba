import asyncio
import aiohttp
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    GIFT_NAMES, GIFT_EMOJIS, GIFT_IDS,
    GIFT_VALUES, SPIN_COSTS
)
from keyboards import (
    get_payment_keyboard,
    get_start_keyboard,
    get_bet_keyboard
)
from utils import (
    spin_roulette,
    generate_animation_sequence,
    is_subscribed
)


class RouletteSpin(StatesGroup):
    """States for the roulette spin process"""
    selecting_bet = State()
    waiting_for_payment = State()


roulette_router = Router()


@roulette_router.callback_query(F.data == "play_game")
async def callback_play_game(callback: CallbackQuery, state: FSMContext):
    """Handler for 'Play Game' button"""
    # Check subscription status
    subscribed = await is_subscribed(callback.from_user.id, callback.bot)

    # Set state
    await state.set_state(RouletteSpin.selecting_bet)

    # Edit message with bet keyboard
    await callback.message.edit_text(
        "🎲 Выберите ставку:",
        reply_markup=get_bet_keyboard()
    )
    await callback.answer()


@roulette_router.callback_query(RouletteSpin.selecting_bet, F.data.startswith("bet_"))
async def process_bet_selection(callback: CallbackQuery, state: FSMContext):
    """Process bet selection and create invoice"""
    # Extract bet amount and type
    _, amount_str = callback.data.split("_")
    amount = int(amount_str)

    # Determine spin type based on amount
    spin_type = {
        25: "basic",
        50: "standard",
        100: "premium"
    }.get(amount, "basic")

    # Store spin details in state
    await state.update_data(spin_type=spin_type, amount=amount)

    # Prepare invoice descriptions
    descriptions = {
        25: "Базовый прокрут за 25 звёзд! Выиграйте подарок!",
        50: "Стандартный прокрут за 50 звёзд! Шанс на ценные подарки!",
        100: "Премиум прокрут за 100 звёзд! Лучшие шансы на редкие подарки!"
    }

    # Prepare prices for invoice
    prices = [LabeledPrice(label="XTR", amount=amount)]

    # Set state to waiting for payment
    await state.set_state(RouletteSpin.waiting_for_payment)

    # Send invoice
    await callback.message.answer_invoice(
        title=f"Прокрут за {amount} звёзд",
        description=descriptions[amount],
        prices=prices,
        provider_token="",  # Для Telegram Stars используем пустую строку
        payload=f"spin_{spin_type}",
        currency="XTR",  # Валюта для Telegram Stars
        reply_markup=get_payment_keyboard(amount),
    )

    await callback.answer()


@roulette_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Pre-checkout handler"""
    await pre_checkout_query.answer(ok=True)


@roulette_router.message(F.successful_payment)
async def success_payment_handler(message: Message, state: FSMContext):
    """Handle successful payment and spin the roulette"""
    # Retrieve spin details from state
    user_data = await state.get_data()
    spin_type = user_data.get('spin_type', 'basic')

    # Get roulette stats from bot's initial data
    roulette_stats = message.bot.initial_data['roulette_stats']

    # Send initial roulette spinning message
    roulette_message = await message.answer("🎡 Рулетка начинает вращение...")

    try:
        # Determine spin result
        result = spin_roulette(spin_type, message.from_user.id, roulette_stats)

        # Generate animation sequence
        animation_sequence = generate_animation_sequence(result)

        # Animate roulette spinning
        for i, gift in enumerate(animation_sequence):
            emoji = GIFT_EMOJIS.get(gift, "🎁")
            gift_name = GIFT_NAMES.get(gift, "Подарок")

            # Update message for animation
            if i == len(animation_sequence) - 1:
                # Final result
                await roulette_message.edit_text(
                    f"🎉 Результат: {emoji} {gift_name} ({GIFT_VALUES.get(gift, 0)} звезд)!"
                )
            else:
                # Intermediate animation
                await roulette_message.edit_text(
                    f"🎡 Рулетка вращается... {emoji} {gift_name}"
                )

                # Wait between animations
                wait_time = 0.3 if i < len(animation_sequence) - 3 else 0.5
                await asyncio.sleep(wait_time)

        # Send gift to user
        gift_id = GIFT_IDS.get(result)
        await send_gift(message, gift_id, result)

        # Get start keyboard
        keyboard = await get_start_keyboard(message.from_user.id)

        # Offer to play again
        await message.answer(
            "Хотите испытать удачу снова?",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Error in roulette spin: {e}")
        await message.answer("Произошла ошибка при розыгрыше. Попробуйте позже.")

    # Clear state
    await state.clear()


async def send_gift(message: Message, gift_id: str, gift_type: str):
    """Send gift to user"""
    # Retrieve user and gift details
    user_id = message.from_user.id
    emoji = GIFT_EMOJIS.get(gift_type, "🎁")
    gift_name = GIFT_NAMES.get(gift_type, "Подарок")

    # Initial gift sending message
    await message.answer(f"Отправляю вам подарок {emoji} {gift_name}...")

    try:
        async with aiohttp.ClientSession() as session:
            # Prepare gift sending URL
            url = f"https://api.telegram.org/bot{message.bot.token}/sendGift"

            # Prepare initial parameters
            params = {
                "user_id": user_id,
                "gift_id": gift_id
            }

            # First attempt to send gift
            async with session.get(url, params=params) as response:
                result = await response.json()

                if result.get("ok"):
                    await message.answer(f"{emoji} Подарок {gift_name} успешно отправлен! ✨")
                    return

                # Handle potential errors
                error_description = result.get('description', 'Неизвестная ошибка')

                # Try with pay_for_upgrade if first attempt fails
                if "STARGIFT_UPGRADE_UNAVAILABLE" in error_description:
                    params["pay_for_upgrade"] = True
                    async with session.get(url, params=params) as pay_response:
                        pay_result = await pay_response.json()

                        if pay_result.get("ok"):
                            await message.answer(f"{emoji} Подарок {gift_name} успешно отправлен! ✨")
                            return

                        # Handle payment upgrade errors
                        pay_error = pay_result.get('description', 'Неизвестная ошибка')
                        await message.answer(
                            f"Не удалось отправить подарок: {pay_error}\n"
                            f"Вы можете получить подарок по ссылке:\n"
                            f"tg://gift?slug={gift_id}"
                        )
                else:
                    # Handle other errors
                    await message.answer(
                        f"Ошибка при отправке подарка: {error_description}\n"
                        f"Вы можете получить подарок по ссылке:\n"
                        f"tg://gift?slug={gift_id}"
                    )

    except Exception as e:
        # Log and handle any unexpected errors
        logging.error(f"Gift sending error: {e}")
        await message.answer(
            f"Произошла ошибка при отправке подарка.\n"
            f"Попробуйте получить его по ссылке:\n"
            f"tg://gift?slug={gift_id}"
        )