import sqlite3

def get_connection():
    return sqlite3.connect("inventory.db")

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            name TEXT PRIMARY KEY,
            stock INTEGER,
            value INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_item(name, stock, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (name, stock, value) VALUES (?, ?, ?)
        ON CONFLICT (name) DO UPDATE SET stock = ?, value = ?
    """, (name, stock, value, stock, value))
    conn.commit()
    conn.close()

def load_all_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_item_from_db(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE name = ?",(name,))
    conn.commit()
    conn.close()

def update_item(current_name, new_name = None, new_stock = None, new_value = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, stock, value FROM items WHERE name = ?", (current_name,))
    item = cursor.fetchone()
    if item is None:
        print("item not found")
        conn.close()
        return False
    name = new_name if new_name is not None else item[0]
    stock = new_stock if new_stock is not None else item[1]
    value = new_value if new_value is not None else item[2]
    cursor.execute("""
        UPDATE items SET name = ?, stock = ?, value = ? WHERE name = ? 
    """, (name, stock, value, current_name))
    conn.commit()
    conn.close()
    print("item updated successfully")
    return True

def get_item_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, stock, value FROM items WHERE name = ?",(name,))
    item = cursor.fetchone()
    conn.close()
    return item