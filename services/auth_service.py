import hashlib
from database.db import connect_db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role):

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )

        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()

def login_user(username, password):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, role, password FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and user[2] == hash_password(password):
        return {
            "id": user[0],
            "role": user[1],
            "username": username
        }

    return None