import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "railway.db")

os.makedirs(DATABASE_DIR, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_user_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_booking_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number TEXT,
            train_name TEXT,
            passenger_name TEXT,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            user_id INTEGER
        )
    """)

    # Add user_id to an existing bookings table if it is missing
    columns = conn.execute(
        "PRAGMA table_info(bookings)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "user_id" not in column_names:
        conn.execute(
            "ALTER TABLE bookings ADD COLUMN user_id INTEGER"
        )

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_bookings_user_id
        ON bookings(user_id)
    """)

    conn.commit()
    conn.close()


create_user_table()
create_booking_table()
