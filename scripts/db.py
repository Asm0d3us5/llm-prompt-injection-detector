import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "../data/scans.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            flagged BOOLEAN NOT NULL,
            category TEXT,
            atlas_id TEXT,
            atlas_name TEXT,
            confidence REAL,
            method TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_scan(text: str, result: dict, atlas_info: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO scans (text, flagged, category, atlas_id, atlas_name, confidence, method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            text,
            result["flagged"],
            result["category"],
            atlas_info.get("id"),
            atlas_info.get("name"),
            result["confidence"],
            result["method"],
            datetime.now(timezone.utc).isoformat(),
        )
    )
    conn.commit()
    conn.close()

def get_history(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM scans").fetchone()["c"]
    flagged = conn.execute("SELECT COUNT(*) as c FROM scans WHERE flagged = 1").fetchone()["c"]
    by_category = conn.execute(
        "SELECT category, COUNT(*) as count FROM scans WHERE flagged = 1 GROUP BY category"
    ).fetchall()
    by_method = conn.execute(
        "SELECT method, COUNT(*) as count FROM scans WHERE flagged = 1 GROUP BY method"
    ).fetchall()
    conn.close()
    return {
        "total_scans": total,
        "total_flagged": flagged,
        "by_category": [dict(r) for r in by_category],
        "by_method": [dict(r) for r in by_method],
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
