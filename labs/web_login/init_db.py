import sqlite3

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

users = [
    ("admin", "admin123"),
    ("user", "password"),
    ("test", "123456")
]

cur.executemany(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    users
)

conn.commit()
conn.close()

print("users.db oluşturuldu")