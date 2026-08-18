import json
from typing import Any, Dict, Optional

import aiosqlite

from aiogram.fsm.storage.base import BaseStorage, StorageKey


class SQLiteStorage(BaseStorage):
    """
    Простое SQLite-хранилище для FSM aiogram 3.x.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS fsm_states (
                    key TEXT PRIMARY KEY,
                    state TEXT,
                    data TEXT DEFAULT '{}',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    def _serialize_key(self, key: StorageKey) -> str:
        parts = [
            str(key.bot_id),
            str(key.chat_id),
            str(key.user_id),
            str(getattr(key, "thread_id", 0) or 0),
            str(getattr(key, "business_connection_id", "") or ""),
        ]

        return ":".join(parts)

    async def set_state(self, key: StorageKey, state: Optional[str]) -> None:
        serialized_key = self._serialize_key(key)

        async with aiosqlite.connect(self.db_path) as db:
            if state is None:
                await db.execute(
                    "DELETE FROM fsm_states WHERE key = ?",
                    (serialized_key,),
                )
            else:
                await db.execute(
                    """
                    INSERT INTO fsm_states (key, state, data)
                    VALUES (?, ?, '{}')
                    ON CONFLICT(key) DO UPDATE SET state = excluded.state
                    """,
                    (serialized_key, state),
                )

            await db.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        serialized_key = self._serialize_key(key)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT state FROM fsm_states WHERE key = ?",
                (serialized_key,),
            ) as cursor:
                row = await cursor.fetchone()

                if row is None:
                    return None

                return row["state"] or None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        serialized_key = self._serialize_key(key)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO fsm_states (key, state, data)
                VALUES (?, NULL, ?)
                ON CONFLICT(key) DO UPDATE SET data = excluded.data
                """,
                (
                    serialized_key,
                    json.dumps(data, ensure_ascii=False),
                ),
            )

            await db.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        serialized_key = self._serialize_key(key)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT data FROM fsm_states WHERE key = ?",
                (serialized_key,),
            ) as cursor:
                row = await cursor.fetchone()

                if row is None:
                    return {}

                try:
                    return json.loads(row["data"] or "{}")
                except json.JSONDecodeError:
                    return {}

    async def close(self) -> None:
        pass
