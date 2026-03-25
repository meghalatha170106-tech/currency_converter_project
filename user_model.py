from models.db import get_db_connection
import hashlib

# Register user
def create_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()

    hashed = hashlib.sha256(password.encode()).hexdigest()

    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

# Login user
def login_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()

    hashed = hashlib.sha256(password.encode()).hexdigest()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = cur.fetchone()
    conn.close()

    return user