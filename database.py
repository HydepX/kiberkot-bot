# database.py
import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    """
    Фундамент Блока 4: новые таблицы + расширение существующей orders.
    Ничего не удаляем — старые данные и сценарии продолжают работать.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Пользователи (с телефоном)
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 2. История сообщений для ИИ
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 3. Запросы на связь с менеджером
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS handovers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 4. Расширяем существующую таблицу orders новыми колонками.
        #    Если колонка уже есть — SQLite кинет ошибку, молча пропускаем.
        for column_sql in (
            "ALTER TABLE orders ADD COLUMN type TEXT",
            "ALTER TABLE orders ADD COLUMN data_json TEXT",
            "ALTER TABLE orders ADD COLUMN phone_snapshot TEXT",
            "ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ):
            try:
                await db.execute(column_sql)
            except Exception:
                pass

        await db.commit()


# --- Вспомогательные функции ---

async def save_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )
        await db.commit()


async def get_recent_messages(user_id: int, limit: int = 5):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT role, content FROM messages
            WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (user_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return list(reversed(rows))


async def create_order(user_id: int, order_type: str, data_json: str, phone: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO orders (user_id, type, data_json, phone_snapshot)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, order_type, data_json, phone),
        )
        await db.commit()
        return cursor.lastrowid


async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT id, type, status, data_json, created_at
            FROM orders WHERE user_id = ? ORDER BY created_at DESC
            """,
            (user_id,),
        ) as cursor:
            return await cursor.fetchall()


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (status, order_id),
        )
        await db.commit()


async def get_all_orders(limit=10, offset=0, status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT id, user_id, type, status, data_json, created_at FROM orders"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()
