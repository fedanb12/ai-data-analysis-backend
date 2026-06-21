import sqlite3
import json
from datetime import datetime

DB_PATH = "analysis.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            row_count INTEGER,
            column_count INTEGER,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question TEXT,
            answer TEXT,
            created_at TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_session(file_name, row_count, column_count):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (file_name, row_count, column_count, created_at)
        VALUES (?, ?, ?, ?)
    ''', (file_name, row_count, column_count, datetime.now().isoformat()))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_sessions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "file_name": r[1],
            "row_count": r[2],
            "column_count": r[3],
            "created_at": r[4]
        }
        for r in rows
    ]

def save_history(session_id, question, answer):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (session_id, question, answer, created_at)
        VALUES (?, ?, ?, ?)
    ''', (session_id, question, answer, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM history WHERE session_id = ? ORDER BY created_at',
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "session_id": r[1],
            "question": r[2],
            "answer": r[3],
            "created_at": r[4]
        }
        for r in rows
    ]