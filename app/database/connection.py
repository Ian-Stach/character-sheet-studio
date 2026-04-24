from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "personajes.db"

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS personajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                raza TEXT,
                clase TEXT,
                edad INTEGER,
                descripcion TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()