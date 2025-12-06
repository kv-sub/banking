# db_postgres.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bank")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # MAIN TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            income REAL NOT NULL,
            loan_amount REAL NOT NULL,
            pan TEXT NOT NULL,
            status TEXT NOT NULL,
            credit_score INTEGER,
            risk_level TEXT,
            decision_reason TEXT,
            llm_explanation TEXT,
            llm_status_explanation TEXT,
            created_at TIMESTAMP NOT NULL
        );
    """)

    # Status history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_status_history (
            id SERIAL PRIMARY KEY,
            application_id TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            changed_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_pan ON loan_applications (pan);")

    # Partial unique index for active PAN
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_active_pan
        ON loan_applications (pan)
        WHERE status IN ('submitted','processing','manual_review');
    """)

    conn.commit()
    conn.close()


def log_status_change(application_id: str, old_status: str | None, new_status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO loan_status_history (application_id, old_status, new_status)
        VALUES (%s, %s, %s)
    """, (application_id, old_status, new_status))
    conn.commit()
    conn.close()


def get_status_history(application_id: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT old_status, new_status, changed_at
        FROM loan_status_history
        WHERE application_id = %s
        ORDER BY changed_at ASC
    """, (application_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def check_active_application(pan: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT application_id FROM loan_applications
        WHERE pan = %s AND status IN ('submitted','processing','manual_review')
        LIMIT 1
    """, (pan,))
    r = cur.fetchone()
    conn.close()
    return bool(r)


def insert_application(app: dict):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO loan_applications
            (application_id, name, age, income, loan_amount, pan, status,
             credit_score, risk_level, decision_reason, llm_explanation,
             llm_status_explanation, created_at)
            VALUES (%(application_id)s, %(name)s, %(age)s, %(income)s, %(loan_amount)s,
                    %(pan)s, %(status)s, %(credit_score)s, %(risk_level)s, %(decision_reason)s,
                    %(llm_explanation)s, %(llm_status_explanation)s, %(created_at)s)
        """, app)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_application(application_id: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM loan_applications WHERE application_id = %s",
        (application_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row
