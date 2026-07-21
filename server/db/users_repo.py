import sqlite3
import asyncio
import os
from typing import Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def _init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with sqlite3.connect(DB_PATH) as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

# אתחול ה-DB בעת טעינת המודול
_init_db()

def _register_user_sync(username: str, password: str) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, rating) VALUES (?, ?, 1200)",
                (username, password)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # משתמש כבר קיים
        return False

def _verify_user_sync(username: str, password: str) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, rating FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

# פונקציות אסינכרוניות לשימוש בשאר חלקי השרת
async def register_user(username: str, password: str) -> bool:
    return await asyncio.to_thread(_register_user_sync, username, password)

async def verify_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_verify_user_sync, username, password)