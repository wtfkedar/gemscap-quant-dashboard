import sqlite3
from pathlib import Path
import threading

DB_PATH = Path("market_data.db")
_lock = threading.Lock()

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ticks (
            timestamp TEXT,
            symbol TEXT,
            price REAL,
            qty REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_tick(ts, symbol, price, qty):
    with _lock:
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO ticks VALUES (?, ?, ?, ?)",
                (ts, symbol, price, qty)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error inserting tick: {e}")

def get_all_ticks():
    with _lock:
        try:
            conn = get_connection()
            rows = conn.execute("SELECT * FROM ticks ORDER BY timestamp DESC LIMIT 100000").fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Error fetching ticks: {e}")
            return []

def get_tick_count():
    with _lock:
        try:
            conn = get_connection()
            count = conn.execute("SELECT COUNT(*) FROM ticks").fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error counting ticks: {e}")
            return 0

def cleanup_old_data(keep_last_n=50000):
    """Keep only the most recent N records"""
    with _lock:
        try:
            conn = get_connection()
            count = conn.execute("SELECT COUNT(*) FROM ticks").fetchone()[0]
            if count > keep_last_n:
                conn.execute(f"""
                    DELETE FROM ticks WHERE rowid NOT IN (
                        SELECT rowid FROM ticks ORDER BY timestamp DESC LIMIT {keep_last_n}
                    )
                """)
                conn.commit()
                print(f"Cleaned up old data, kept {keep_last_n} records")
            conn.close()
        except Exception as e:
            print(f"Error cleaning up data: {e}")

def clear_all_data():
    """Clear all data from database"""
    with _lock:
        try:
            conn = get_connection()
            conn.execute("DELETE FROM ticks")
            conn.commit()
            conn.close()
            print("All data cleared")
        except Exception as e:
            print(f"Error clearing data: {e}")
