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
    Returns a dict with status and price info for notifications.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    item_id = item_data['item_id']
    name = item_data['name']
    price = item_data['price']
    url = item_data['url']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if item exists
    cursor.execute("SELECT current_price, lowest_price FROM products WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()

    result = {
        "item_id": item_id,
        "name": name,
        "new_price": price,
        "old_price": 0,
        "lowest_price": price,
        "status": "new_item",
        "url": url
    }

    if row is None:
        # New item
        cursor.execute('''
            INSERT INTO products (item_id, name, current_price, current_date, lowest_price, lowest_date, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, price, now, price, now, url))
        print(f"Added new product: {name[:30]}... at ₹{price}")
    else:
        # Existing item
        old_price, lowest_price = row
        result["old_price"] = old_price
        result["lowest_price"] = lowest_price

        if price < lowest_price:
            # New all-time low!
            status = "new_lowest"
            cursor.execute('''
                UPDATE products 
                SET current_price = ?, current_date = ?, lowest_price = ?, lowest_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (price, now, price, now, name, url, item_id))
            print(f"New lowest price for {name[:30]}...! recorded: ₹{price}")
            result["lowest_price"] = price
        elif price < old_price:
            status = "price_decrease"
            cursor.execute('''
                UPDATE products 
                SET current_price = ?, current_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (price, now, name, url, item_id))
            print(f"Price dropped for {name[:30]}... from ₹{old_price} to ₹{price}")
        elif price > old_price:
            status = "price_increase"
            cursor.execute('''
                UPDATE products 
                SET current_price = ?, current_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (price, now, name, url, item_id))
            print(f"Price increased for {name[:30]}... from ₹{old_price} to ₹{price}")
        else:
            status = "no_change"
            cursor.execute('''
                UPDATE products 
                SET current_date = ?, name = ?, url = ?
                WHERE item_id = ?
            ''', (now, name, url, item_id))

        result["status"] = status

    conn.commit()
    conn.close()
    return result

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
