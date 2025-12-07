# main.py
from fastapi import FastAPI, HTTPException
import os
from models import LoanApplicationCreate, LoanApplicationOut, ManualReviewRequest, ChatRequest
from services import generate_application_data
from fastapi.middleware.cors import CORSMiddleware
from db_postgres import (
    init_db,
    insert_application,
    get_application,
    get_status_history,
    record_manual_review,
    log_status_change,
)
from agent import run_agent
from llm_service import generate_full_explanation, generate_chat_response
from dotenv import load_dotenv
from db_postgres import get_connection

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = FastAPI(title="Bank Loan STP API with GenAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allow all frontend origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],            # All headers
)

init_db()

# ============================================================
# CUSTOMER: CREATE APPLICATION
# ============================================================
@app.post("/loan/", response_model=LoanApplicationOut)
def create_loan_application(request: LoanApplicationCreate):
    try:
        data = generate_application_data(request)
        insert_application(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = {
        **data,
        "history": get_status_history(data["application_id"])
    }
    return LoanApplicationOut(**record)


# ============================================================
# OFFICER DASHBOARD: GET ALL APPLICATIONS
# ============================================================
@app.get("/loan/all")
def get_all_applications():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM loan_applications ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()

    return rows


# ============================================================
# OFFICER DASHBOARD: GET ALL MANUAL REVIEW APPLICATIONS
# ============================================================
@app.get("/loan/pending_review")
def pending_manual_review():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM loan_applications
        WHERE status = 'manual_review'
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()

    return rows


# ============================================================
# CUSTOMER: GET APPLICATION STATUS
# ============================================================
@app.get("/loan/{application_id}", response_model=LoanApplicationOut)
def get_application_status(application_id: str):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    row["history"] = get_status_history(application_id)
    return LoanApplicationOut(**row)


# ============================================================
# CUSTOMER: ON-DEMAND LLM EXPLANATION
# ============================================================
@app.get("/loan/{application_id}/explain")
def explain_application(application_id: str):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    history = get_status_history(application_id)

    agent_sim = {
        "credit_score": row["credit_score"],
        "risk_level": row["risk_level"],
        "decision_reason": row["decision_reason"]
    }

    return generate_full_explanation(row, agent_sim, history)


# ============================================================
# CUSTOMER: CHAT WITH LLM ABOUT APPLICATION
# ============================================================
@app.post("/loan/{application_id}/chat")
def chat_about_application(application_id: str, req: ChatRequest):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    history = get_status_history(application_id)

    return generate_chat_response(row, history, req.message)


# ============================================================
# OFFICER: MANUAL REVIEW APPROVE/REJECT
# ============================================================
@app.put("/loan/{application_id}/review")
def review_application(application_id: str, req: ManualReviewRequest):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    if row["status"] != "manual_review":
        raise HTTPException(status_code=400, detail="Application is not pending manual review")

    action = req.action.lower()
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be approve/reject")

    new_status = "approved" if action == "approve" else "rejected"

    record_manual_review(application_id, req.officer, new_status, req.notes)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE loan_applications
        SET status=%s, officer_notes=%s, reviewed_by=%s
        WHERE application_id=%s
    """, (new_status, req.notes, req.officer, application_id))
    conn.commit()
    conn.close()

    log_status_change(application_id, "manual_review", new_status)

    updated = get_application(application_id)
    updated["history"] = get_status_history(application_id)
    return updated


