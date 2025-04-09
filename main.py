import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from utils import load_initial_data
from handlers.start import start_router
from handlers.admin import admin_router
from handlers.roulette import roulette_router
from handlers.broadcast import broadcast_router

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Load initial data
    initial_data = load_initial_data()

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_routers(
        start_router,
        admin_router,
        roulette_router,
        broadcast_router
    )

    # Attach initial data to bot
    bot.initial_data = initial_data

    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Close bot session
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())