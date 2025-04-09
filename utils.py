import os
import json
import logging
import random
from datetime import datetime
from typing import Dict, Set, Any

from config import (
    USERS_FILE, REFERRALS_FILE, CREDITED_REFERRALS_FILE,
    STATS_FILE, ADMIN_IDS, GIFT_VALUES, GIFT_NAMES,
    GIFT_EMOJIS, SPIN_COSTS
)


def get_current_timestamp() -> str:
    """Get current formatted timestamp."""
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def load_json_data(filename: str) -> dict:
    """Load data from a JSON file."""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            logging.error(f"Error reading file {filename}: {e}")
    return {}


def save_json_data(filename: str, data: dict) -> None:
    """Save data to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error writing to file {filename}: {e}")


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS


def add_user(users_data: Dict[str, Dict[str, Any]], user_id: int, username: str) -> None:
    """Add or update a user in the database."""
    users_data[str(user_id)] = {
        "username": username,
        "status": "active",
        "joined_at": get_current_timestamp()
    }
    save_json_data(USERS_FILE, users_data)


def remove_user(users_data: Dict[str, Dict[str, Any]], user_id: int) -> None:
    """Mark a user as removed."""
    if str(user_id) in users_data:
        users_data[str(user_id)]["status"] = "removed"
        save_json_data(USERS_FILE, users_data)


def spin_roulette(spin_type: str, user_id: int, roulette_stats: Dict[str, Dict[str, Any]]) -> str:
    """Определяет результат вращения рулетки"""
    user_id_str = str(user_id)

    # Инициализация статистики пользователя, если её ещё нет
    if user_id_str not in roulette_stats:
        roulette_stats[user_id_str] = {
            "total_spins": 0,
            "spins_without_win": 0,
            "total_spent": 0,
            "total_won": 0,
            "gifts": {}
        }

    # Увеличиваем счетчик спинов
    roulette_stats[user_id_str]["total_spins"] += 1
    roulette_stats[user_id_str]["total_spent"] += SPIN_COSTS.get(spin_type, 0)

    # Счетчик спинов без равноценного или выигрышного результата
    spins_without_win = roulette_stats[user_id_str]["spins_without_win"]

    # Определение таблицы вероятностей в зависимости от типа спина
    # и счетчика неудачных спинов
    boost_factor = 1.0
    if spins_without_win >= 5:
        boost_factor = 3.0  # Значительно увеличиваем шансы
    elif spins_without_win >= 4:
        boost_factor = 2.0  # Умеренно увеличиваем шансы

    if spin_type == "basic":  # 25 звезд
        probabilities = {
            "heart": 70 / boost_factor,
            "bear": 25 / boost_factor,
            "rose": 4.5 * boost_factor,
            "cake": 0.5 * boost_factor,
            "bouquet": 0,
            "rocket": 0,
            "trophy": 0,
            "ring": 0,
            "diamond": 0
        }
    elif spin_type == "standard":  # 50 звезд
        probabilities = {
            "heart": 40 / boost_factor,
            "bear": 30 / boost_factor,
            "rose": 20,  # Не меняем этот шанс
            "cake": 3 * boost_factor,
            "bouquet": 3 * boost_factor,
            "rocket": 3 * boost_factor,
            "trophy": 0.9 * boost_factor,
            "ring": 0.09 * boost_factor,
            "diamond": 0.01 * boost_factor
        }
    else:  # premium - 100 звезд
        probabilities = {
            "heart": 20 / boost_factor,
            "bear": 20 / boost_factor,
            "rose": 30 / boost_factor,
            "cake": 8 * boost_factor,
            "bouquet": 8 * boost_factor,
            "rocket": 8 * boost_factor,
            "champagne": 4 * boost_factor,
            "trophy": 1.5 * boost_factor,
            "ring": 0.4 * boost_factor,
            "diamond": 0.1 * boost_factor
        }

    # Создание массива для взвешенного выбора
    items = list(probabilities.keys())
    weights = list(probabilities.values())

    # Выбор результата
    result = random.choices(items, weights=weights, k=1)[0]

    # Обновляем статистику пользователя
    gift_value = GIFT_VALUES.get(result, 0)
    spin_cost = SPIN_COSTS.get(spin_type, 0)

    roulette_stats[user_id_str]["total_won"] += gift_value

    # Обновляем счетчик подарков
    if result not in roulette_stats[user_id_str]["gifts"]:
        roulette_stats[user_id_str]["gifts"][result] = 0
    roulette_stats[user_id_str]["gifts"][result] += 1

    # Если выигрыш равноценный или больше стоимости спина - сбрасываем счетчик
    if gift_value >= spin_cost:
        roulette_stats[user_id_str]["spins_without_win"] = 0
    else:
        roulette_stats[user_id_str]["spins_without_win"] += 1

    # Сохраняем статистику
    save_json_data(STATS_FILE, roulette_stats)

    return result


def generate_animation_sequence(final_result: str) -> list:
    """Генерирует последовательность подарков для анимации"""
    sequence = []
    all_gifts = list(GIFT_VALUES.keys())

    # 10 элементов для анимации вращения
    for i in range(10):
        if i < 7:
            # Случайные призы
            sequence.append(random.choice(all_gifts))
        else:
            # Ближе к концу чаще показываем дорогие призы и финальный результат
            if random.random() < 0.3:
                sequence.append(final_result)
            else:
                expensive_gifts = ["trophy", "ring", "diamond", "cake", "bouquet"]
                sequence.append(random.choice(expensive_gifts))

    # Финальный результат
    sequence.append(final_result)
    return sequence


def load_initial_data():
    """Initialize data from files."""
    users_data = load_json_data(USERS_FILE)
    referral_data = load_json_data(REFERRALS_FILE)
    credited_referrals = set(load_json_data(CREDITED_REFERRALS_FILE).get("credited", []))
    roulette_stats = load_json_data(STATS_FILE)

    logging.info(
        f"Loaded {len(users_data)} users, {len(referral_data)} referrals, "
        f"{len(credited_referrals)} credited referrals, {len(roulette_stats)} roulette stats"
    )

    return {
        "users_data": users_data,
        "referral_data": referral_data,
        "credited_referrals": credited_referrals,
        "roulette_stats": roulette_stats
    }


async def is_subscribed(user_id: int, bot, chat_id: str = "@GiftsForFree_News"):
    """
    Check if a user is subscribed to a specific channel

    :param user_id: Telegram user ID
    :param bot: Telegram Bot instance
    :param chat_id: Channel username to check subscription
    :return: Boolean indicating subscription status
    """
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False
