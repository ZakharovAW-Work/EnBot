import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import db
from scheduler import setup_scheduler
from handlers import cards, dialog, common

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import os
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN=os.getenv("TOKEN")

async def main():
    await db.init()
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()                 # в продакшене — RedisStorage
    dp = Dispatcher(storage=storage)

    # Порядок важен: сначала роутеры с FSM-состояниями, «слушатель» последним
    dp.include_router(cards.router)
    dp.include_router(dialog.router)
    dp.include_router(common.router)

    scheduler = setup_scheduler(bot)
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())