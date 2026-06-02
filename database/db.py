import os
import psycopg2
import streamlit as st

def connect_db():

    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )

def init_db():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(20)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs(
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id SERIAL PRIMARY KEY,
        applicant_name TEXT,
        resume_text TEXT,
        job_id INTEGER,
        score INTEGER DEFAULT 0,
        reasoning TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()
    