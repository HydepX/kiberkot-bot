import os

from dotenv import load_dotenv


load_dotenv("/opt/kiberkot/.env")
load_dotenv(".env")


BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "kiberkot.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Проверь .env файл.")
