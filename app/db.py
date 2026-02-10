import sqlite3
from datetime import date


DB_PATH = "attendance.db"


def get_connection():
    return sqlite3.connect(
        DB_PATH,
        timeout=5,
        check_same_thread=False
    )


def init_db():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица посещаемости
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                day DATE NOT NULL,
                status TEXT NOT NULL,
                proof_file_id TEXT,
                proof_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, day)
            );

        """)

        # WAL режим (очень важно для SQLite + async)
        cursor.execute("PRAGMA journal_mode=WAL;")

        conn.commit()
    finally:
        conn.close()


def get_user(user_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, name FROM users WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def add_user(user_id: int, name: str, username: str | None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)",
            (user_id, name, username)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def add_attendance(
    user_id: int,
    status: str,
    proof_file_id: str | None = None,
    proof_type: str | None = None
) -> bool:
    today = date.today().isoformat()
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (user_id, day, status, proof_file_id, proof_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, today, status, proof_file_id, proof_type)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_excused_attendance():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                u.name,
                a.day,
                a.proof_file_id,
                a.proof_type
            FROM attendance a
            JOIN users u ON u.user_id = a.user_id
            WHERE a.status = 'excused'
            ORDER BY a.day DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()
