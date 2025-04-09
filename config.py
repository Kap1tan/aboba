import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
BOT_TOKEN = "7921309251:AAGnoTXuH4CPpzZmvdlSlEUSoK9wZ70gEog"

# Admin IDs
ADMIN_IDS = [804644988]  # Replace with your actual admin IDs

# Files for data storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
REFERRALS_FILE = os.path.join(DATA_DIR, "referrals.json")
CREDITED_REFERRALS_FILE = os.path.join(DATA_DIR, "credited.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Roulette constants
GIFT_VALUES = {
    "heart": 15,  # Сердце
    "bear": 15,  # Медведь
    "rose": 25,  # Роза
    "cake": 50,  # Торт
    "bouquet": 50,  # Букет
    "rocket": 50,  # Ракета
    "champagne": 50,  # Шампанское
    "trophy": 100,  # Трофей
    "ring": 100,  # Кольцо
    "diamond": 100  # Бриллиант
}

# ID подарков в Telegram
GIFT_IDS = {
    "heart": "5170145012310081615",  # Сердце
    "bear": "5170233102089322756",  # Медведь
    "rose": "5168103777563050263",  # Роза
    "cake": "5170144170496491616",  # Торт
    "bouquet": "5170314324215857265",  # Букет
    "rocket": "5170564780938756245",  # Ракета
    "champagne": "6028601630662853006",  # Шампанское
    "trophy": "5168043875654172773",  # Трофей
    "ring": "5170690322832818290",  # Кольцо
    "diamond": "5170521118301225164"  # Бриллиант
}

# Эмодзи для подарков
GIFT_EMOJIS = {
    "heart": "❤️",
    "bear": "🧸",
    "rose": "🌹",
    "cake": "🎂",
    "bouquet": "💐",
    "rocket": "🚀",
    "champagne": "🍾",
    "trophy": "🏆",
    "ring": "💍",
    "diamond": "💎"
}

# Названия подарков на русском
GIFT_NAMES = {
    "heart": "Сердце",
    "bear": "Медведь",
    "rose": "Роза",
    "cake": "Торт",
    "bouquet": "Букет",
    "rocket": "Ракета",
    "champagne": "Шампанское",
    "trophy": "Трофей",
    "ring": "Кольцо",
    "diamond": "Бриллиант"
}

# Стоимость спинов
SPIN_COSTS = {
    "basic": 25,
    "standard": 50,
    "premium": 100
}
