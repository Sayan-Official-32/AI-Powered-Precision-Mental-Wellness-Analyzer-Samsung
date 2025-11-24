import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings


def get_connection():
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                reason TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_interaction(channel: str, payload: Dict[str, Any]) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO interactions(channel, payload, created_at) VALUES (?, ?, ?)",
            (channel, json.dumps(payload), datetime.utcnow().isoformat()),
        )
        conn.commit()


def log_alert(level: str, reason: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO alerts(level, reason, metadata, created_at) VALUES (?, ?, ?, ?)",
            (level, reason, json.dumps(metadata or {}), datetime.utcnow().isoformat()),
        )
        conn.commit()


# Ensure the database file exists on import for development servers.
Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
