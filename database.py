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

def upsert_product(item_data):
    """
    Inserts a new product or updates an existing one.
    If the current price is lower than the lowest recorded price, updates lowest price.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    item_id = item_data['item_id']
    name = item_data['name']
    price = item_data['price']
    url = item_data['url']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if item exists
    cursor.execute("SELECT lowest_price FROM products WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()

    if row is None:
        # New item
        cursor.execute('''
            INSERT INTO products (item_id, name, current_price, current_date, lowest_price, lowest_date, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, price, now, price, now, url))
        print(f"Added new product: {name[:30]}... at ₹{price}")
    else:
        # Existing item
        lowest_price = row[0]
        if price < lowest_price:
            # New all-time low!
            cursor.execute('''
                UPDATE products 
                SET current_price = ?, current_date = ?, lowest_price = ?, lowest_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (price, now, price, now, name, url, item_id))
            print(f"New lowest price for {name[:30]}...! recorded: ₹{price}")
        else:
            # Just update current price
            cursor.execute('''
                UPDATE products 
                SET current_price = ?, current_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (price, now, name, url, item_id))
            print(f"Updated current price for {name[:30]}... at ₹{price}")

    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
