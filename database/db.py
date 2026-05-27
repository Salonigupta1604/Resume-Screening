import sqlite3

DB_NAME = "database/recruiter.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # JOBS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    # APPLICATIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_name TEXT,
        resume_text TEXT,
        job_id INTEGER,
        score INTEGER DEFAULT 0,
        reasoning TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()