import sqlite3
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

def create_sales_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity INTEGER,
            price_at_sale INTEGER,
            timestamp TEXT
)
    """)
    conn.commit()
    conn.close()

def record_sale(item_name, quantity, price_at_sale):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (item_name, quantity, price_at_sale, timestamp)
        VALUES (?, ?, ?, ?)
    """, (item_name, quantity, price_at_sale, timestamp))
    conn.commit()
    conn.close()

def get_all_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,      
            email TEXT UNIQUE NOT NULL,  
            dob TEXT NOT NULL,            
            created_at TEXT               
        )
    """)
    conn.commit()
    conn.close()

def create_user(username, password_hash, full_name, email, dob, timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, email, dob, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, full_name, email, dob, timestamp))
        conn.commit()
        return True
    except Exception as e:
        print("error: ", e)
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, full_name, email, dob, created_at FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, full_name, email, dob, created_at FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def delete_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users   where   username = ?", ("employee", ))
    cursor.execute("DELETE FROM users   where   username = ?", ("uname", ))
    conn.commit()
    conn.close()



