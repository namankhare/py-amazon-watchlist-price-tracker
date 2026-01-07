import sqlite3
from datetime import datetime

DB_NAME = "amazon_watchlist.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            current_price REAL,
            current_date TEXT,
            lowest_price REAL,
            lowest_date TEXT,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
