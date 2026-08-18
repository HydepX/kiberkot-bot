import os

from dotenv import load_dotenv


# Пытаемся загрузить env из продакшен-пути и из локального файла.
load_dotenv("/opt/kiberkot/.env")
load_dotenv(".env")


BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "kiberkot.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Проверь .env файл.")
