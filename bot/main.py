import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config, db
from scheduler import setup_scheduler
from handlers import cards, dialog, common

async def main():
    await db.init()
    bot = Bot(config.TOKEN, parse_mode="HTML")
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