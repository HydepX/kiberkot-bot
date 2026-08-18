import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан. Проверь файл .env или переменные окружения.")

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

TEXT_START = (
    "Мяу, боец! 🟢 Я <b>КиберКот</b>, твой личный эксперт по периферии Razer.\n\n"
    "Помогу собрать имбовый сетап под твой стиль игры, любимые жанры и бюджет. "
    "Никакой воды — только топовые девайсы, которые решают.\n\n"
    "Жми /help, чтобы узнать, чем я могу помочь, или сразу напиши, что ищем!"
)

TEXT_HELP = (
    "<b>Чем могу помочь? 😼</b>\n\n"
    "Я знаю всё о 5 флагманах Razer:\n"
    "🖱 <b>Viper V4 Pro</b> — скорость и точность\n"
    "⌨️ <b>Huntsman V3 Pro</b> — аналоговые свитчи для хайп-мува\n"
    "🎧 <b>BlackShark V2 Pro</b> — позиционирование звука 360°\n"
    "🔥 <b>Firefly V2 Pro</b> — RGB и идеальное скольжение\n"
    "🎤 <b>Seiren V3 Mini</b> — чистый звук для стримов\n\n"
    "<b>Что я умею:</b>\n"
    "1️⃣ Подобрать сетап под игру (CS2, Dota 2, Valorant и др.)\n"
    "2️⃣ Собрать периферию под бюджет\n"
    "3️⃣ Рассказать про фишки конкретных девайсов\n\n"
    "Просто напиши мне, во что играешь и что ищешь! 🚀"
)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(TEXT_START, parse_mode="HTML")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(TEXT_HELP, parse_mode="HTML")


@dp.message()
async def fallback(message: types.Message):
    await message.answer(
        "Понял тебя! 🟢 Пока я работаю в режиме тестирования и понимаю только команды /start и /help. "
        "Полноценный подбор сетапов Razer скоро будет доступен!"
    )


async def main():
    bot = Bot(token=BOT_TOKEN)

    commands = [
        BotCommand(command="start", description="Приветствие и начало работы"),
        BotCommand(command="help", description="Список команд и помощь"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
