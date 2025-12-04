from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid, datetime
from db import init_db, insert_application, get_application
from models import LoanApplicationIn, LoanApplicationOut
from utils import get_credit_score

app = FastAPI(title="Loan STP - Day 1 (Prototype)")

# initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

@app.post("/loan/apply", response_model=LoanApplicationOut)
def apply_loan(payload: LoanApplicationIn):
    # basic server-side validations
    if payload.loan_amount <= 0 or payload.income <= 0:
        raise HTTPException(status_code=400, detail="income and loan_amount must be > 0")
    application_id = "ln_" + uuid.uuid4().hex[:12]
    created_at = datetime.datetime.utcnow().isoformat() + "Z"
    # call a mock credit score function (simple)
    credit_score = get_credit_score(payload.pan)
    record = {
        "application_id": application_id,
        "name": payload.name,
        "age": payload.age,
        "income": payload.income,
        "loan_amount": payload.loan_amount,
        "pan": payload.pan,
        "status": "submitted",
        "credit_score": credit_score,
        "created_at": created_at
    }
    insert_application(record)
    return LoanApplicationOut(**record)

@app.get("/loan/{application_id}", response_model=LoanApplicationOut)
def get_application_status(application_id: str):
    rec = get_application(application_id)
    if not rec:
        raise HTTPException(status_code=404, detail="application not found")
    return LoanApplicationOut(**rec)
