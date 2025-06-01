import sqlite3

DB_PATH = "mydb.sqlite"


def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    signup_data TEXT NOT NULL,
    email TEXT NOT NULL
    )
              """)
    c.executemany(
        """
    INSERT INTO users (name, signup_data, email) VALUES (?, ?, ?)
    """,
        [
            ("Alice", "2021-01-05", "alice@example.com"),
            ("Boby", "2023-01-20", "boby@example.com"),
            ("Charlie", "2023-02-15", "charlie@example.com"),
            ("Diana", "2023-05-22", "diana@example.com"),
            ("Eve", "2024-12-31", "eve@example.com"),
        ],
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
