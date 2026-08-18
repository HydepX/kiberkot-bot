import json

import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    """
    Создаёт таблицы, если их ещё нет.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                order_type TEXT NOT NULL,
                payload TEXT DEFAULT '{}',
                name TEXT,
                phone TEXT,
                city TEXT,
                comment TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def save_request(
    user_id: int,
    username: str | None,
    order_type: str,
    payload: dict | None = None,
    name: str | None = None,
    phone: str | None = None,
    city: str | None = None,
    comment: str | None = None,
) -> int:
    """
    Сохраняет заявку в SQLite.

    order_type:
    - setup
    - item
    - return
    - question
    """
    payload_json = json.dumps(payload or {}, ensure_ascii=False)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO orders (
                user_id,
                username,
                order_type,
                payload,
                name,
                phone,
                city,
                comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                order_type,
                payload_json,
                name,
                phone,
                city,
                comment,
            ),
        )

        await db.commit()

        return cursor.lastrowid
