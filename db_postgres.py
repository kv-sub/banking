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
            created_at TIMESTAMP NOT NULL
        );
    """)

    # Index for PAN lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pan ON loan_applications (pan);")

    # Partial unique index: block duplicate active applications while in 'submitted' or 'processing'
    # Postgres supports partial indexes
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_active_pan
        ON loan_applications (pan)
        WHERE status IN ('submitted','processing');
    """)

    conn.commit()
    conn.close()


def check_active_application(pan: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT application_id FROM loan_applications
        WHERE pan = %s AND status IN ('submitted','processing')
        LIMIT 1
    """, (pan,))
    r = cur.fetchone()
    conn.close()
    return bool(r)


def insert_application(app: dict):
    """
    Insert a complete application record.
    app should contain all necessary keys:
      application_id, name, age, income, loan_amount, pan, status,
      credit_score, risk_level, decision_reason, created_at, (optional) llm_explanation
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Prevent duplicate active applications per PAN (double check)
        cur.execute("""
            SELECT application_id FROM loan_applications
            WHERE pan = %s AND status IN ('submitted','processing')
            LIMIT 1
        """, (app['pan'],))
        existing = cur.fetchone()
        if existing:
            raise Exception(f"Active application already exists for PAN {app['pan']}")

        cur.execute("""
            INSERT INTO loan_applications
            (application_id, name, age, income, loan_amount, pan, status,
             credit_score, risk_level, decision_reason, llm_explanation, created_at)
            VALUES (%(application_id)s, %(name)s, %(age)s, %(income)s, %(loan_amount)s,
                    %(pan)s, %(status)s, %(credit_score)s, %(risk_level)s, %(decision_reason)s, %(llm_explanation)s, %(created_at)s)
        """, {
            "application_id": app["application_id"],
            "name": app["name"],
            "age": app["age"],
            "income": app["income"],
            "loan_amount": app["loan_amount"],
            "pan": app["pan"],
            "status": app["status"],
            "credit_score": app.get("credit_score"),
            "risk_level": app.get("risk_level"),
            "decision_reason": app.get("decision_reason"),
            "llm_explanation": app.get("llm_explanation"),
            "created_at": app["created_at"],
        })
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


def update_application(application_id: str, updates: dict):
    """
    updates: dict of column -> value to update
    """
    if not updates:
        return
    conn = get_connection()
    cur = conn.cursor()
    set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values())
    values.append(application_id)
    sql = f"UPDATE loan_applications SET {set_clause} WHERE application_id = %s"
    cur.execute(sql, values)
    conn.commit()
    conn.close()
