import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, DB_PATH
from db import init_db
from database import init_db as init_db_v2
from storage import SQLiteStorage
from handlers import all_routers


async def main():
    logging.basicConfig(level=logging.INFO)

    # Старые таблицы (заявки Блока 2)
    await init_db()
    # Фундамент Блока 4: users, messages, handovers + новые колонки orders
    await init_db_v2()

    storage = SQLiteStorage(DB_PATH)
    await storage.init()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_routers(*all_routers)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
