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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            income REAL NOT NULL,
            loan_amount REAL NOT NULL,
            pan TEXT NOT NULL,
            status TEXT NOT NULL,
            credit_score INTEGER NOT NULL,
            risk_level TEXT,
            decision_reason TEXT,
            created_at TIMESTAMP NOT NULL
        );
    """)

    # Index for PAN lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pan ON loan_applications (pan);")

    # Optional: partial unique index to block duplicate active applications
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_active_pan
        ON loan_applications (pan)
        WHERE status = 'submitted';
    """)

    conn.commit()
    conn.close()


def insert_application(app):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check if active application already exists
        cur.execute("""
            SELECT application_id FROM loan_applications
            WHERE pan = %s AND status = 'submitted'
        """, (app['pan'],))
        existing = cur.fetchone()

        if existing:
            raise Exception(f"Active application already exists for PAN {app['pan']}")

        # Insert new application
        cur.execute("""
            INSERT INTO loan_applications
            (application_id, name, age, income, loan_amount, pan, status,
             credit_score, risk_level, decision_reason, created_at)
            VALUES (%(application_id)s, %(name)s, %(age)s, %(income)s, %(loan_amount)s,
                    %(pan)s, %(status)s, %(credit_score)s, %(risk_level)s, %(decision_reason)s, %(created_at)s)
        """, app)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_application(application_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM loan_applications WHERE application_id = %s",
        (application_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row
