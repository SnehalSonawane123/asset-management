import sqlite3
import pandas as pd

DB_FILE = "assets.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        with open("setup.sql", "r") as f:
            conn.executescript(f.read())
        conn.commit()

def fetch_all() -> pd.DataFrame:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()
    if rows:
        return pd.DataFrame([dict(r) for r in rows])
    return pd.DataFrame(columns=["id","name","category","quantity","location","status","created_at"])

def fetch_by_id(aid: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (aid,)).fetchone()
    return dict(row) if row else None

def insert_asset(name: str, category: str, quantity: int, location: str, status: str) -> int:
    """Insert a new asset. Returns the new row's id."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO assets (name, category, quantity, location, status) VALUES (?,?,?,?,?)",
            (name.strip(), category, quantity, location.strip(), status)
        )
        conn.commit()
        return cur.lastrowid

def update_asset(aid: int, name: str, category: str, quantity: int, location: str, status: str) -> bool:
    """Update an existing asset. Returns True if a row was affected."""
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE assets SET name=?, category=?, quantity=?, location=?, status=? WHERE id=?",
            (name.strip(), category, quantity, location.strip(), status, aid)
        )
        conn.commit()
        return cur.rowcount > 0

def delete_asset(aid: int) -> bool:
    """Delete an asset by id. Returns True if a row was affected."""
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM assets WHERE id = ?", (aid,))
        conn.commit()
        return cur.rowcount > 0
