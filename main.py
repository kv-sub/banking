# main.py
from fastapi import FastAPI, HTTPException
import os
from models import LoanApplicationCreate, LoanApplicationOut, ManualReviewRequest
from services import generate_application_data
from db_postgres import (
    init_db,
    insert_application,
    get_application,
    get_status_history,
    record_manual_review,
    log_status_change
)
from agent import run_agent
from llm_service import generate_full_explanation
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = FastAPI(title="Bank Loan STP API with GenAI")

init_db()


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


@app.get("/loan/{application_id}", response_model=LoanApplicationOut)
def get_application_status(application_id: str):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    row["history"] = get_status_history(application_id)
    return LoanApplicationOut(**row)


# 🔥 NEW — On-Demand LLM Explanation
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

    result = generate_full_explanation(row, agent_sim, history)
    return result


# 🔥 Manual Review Approve/Reject
@app.put("/loan/{application_id}/review")
def review_application(application_id: str, req: ManualReviewRequest):
    row = get_application(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")

    if row["status"] != "manual_review":
        raise HTTPException(status_code=400, detail="Application is not pending manual review")

    # Normalize and validate action
    action = req.action.lower()
    if action not in ("approve", "reject"):
        raise HTTPException(
            status_code=400,
            detail="Action must be 'approve' or 'reject'"
        )

    # Convert to final system status
    new_status = "approved" if action == "approve" else "rejected"

    # Save officer audit info
    record_manual_review(application_id, req.officer, new_status, req.notes)

    # Update main loan record
    from db_postgres import get_connection
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE loan_applications
        SET status=%s, officer_notes=%s, reviewed_by=%s
        WHERE application_id=%s
    """, (new_status, req.notes, req.officer, application_id))

    conn.commit()
    conn.close()

    # Log status transition
    log_status_change(application_id, "manual_review", new_status)

    updated = get_application(application_id)
    updated["history"] = get_status_history(application_id)
    return updated
