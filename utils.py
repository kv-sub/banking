# utils.py
import random
from datetime import datetime
from db_postgres import get_connection

def get_or_update_credit_score(pan: str, income: float, loan_amount: float):
    conn = get_connection()
    cur = conn.cursor()

    # Check if credit profile exists
    cur.execute("SELECT credit_score, last_updated FROM credit_profile WHERE pan=%s", (pan,))
    row = cur.fetchone()

    # FIRST TIME PAN → Assign new score
    if not row:
        score = random.randint(600, 780)
        cur.execute("""
            INSERT INTO credit_profile (pan, credit_score, last_updated)
            VALUES (%s, %s, NOW())
        """, (pan, score))
        conn.commit()
        conn.close()
        return score

    score, last_updated = row

    # RULE 1: multiple loans within 30 days → -30
    cur.execute("""
        SELECT COUNT(*)
        FROM loan_applications
        WHERE pan=%s AND created_at > NOW() - INTERVAL '30 days'
    """, (pan,))
    count_recent = cur.fetchone()[0]

    if count_recent > 1:
        score -= 30

    # RULE 2: large loan > income * 3 → -20
    if loan_amount > income * 3:
        score -= 20

    # Clamp limits
    score = max(500, min(score, 800))

    # Update DB
    cur.execute("""
        UPDATE credit_profile
        SET credit_score=%s, last_updated=NOW()
        WHERE pan=%s
    """, (score, pan))

    conn.commit()
    conn.close()

    return score
