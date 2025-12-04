import sqlite3
from datetime import datetime

DB_NAME = "bank.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications (
        application_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        income REAL,
        loan_amount REAL,
        pan TEXT,
        status TEXT,
        credit_score INTEGER,
        created_at TEXT
    );
    """)

    conn.commit()
    conn.close()


def insert_application(app):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO loan_applications 
        (application_id, name, age, income, loan_amount, pan, status, credit_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            app["application_id"],
            app["name"],
            app["age"],
            app["income"],
            app["loan_amount"],
            app["pan"],
            app["status"],
            app["credit_score"],
            app["created_at"],
        ),
    )

    conn.commit()
    conn.close()


def get_application(application_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT application_id, name, age, income, loan_amount, pan,
               status, credit_score, created_at
        FROM loan_applications
        WHERE application_id = ?
    """, (application_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    # Convert tuple -> dict
    return {
        "application_id": row[0],
        "name": row[1],
        "age": row[2],
        "income": row[3],
        "loan_amount": row[4],
        "pan": row[5],
        "status": row[6],
        "credit_score": row[7],
        "created_at": row[8],
    }

