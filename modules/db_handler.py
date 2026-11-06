import sqlite3
import pandas as pd

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            type TEXT,
            category TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(date, desc, amount, t_type, category, notes=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (date, description, amount, type, category, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, desc, amount, t_type, category, notes))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
    conn.close()
    return df