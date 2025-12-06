# models.py
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# STATUS HISTORY MODEL
# ============================================================
class StatusChange(BaseModel):
    old_status: str | None = Field(None, example="submitted")
    new_status: str = Field(..., example="processing")
    changed_at: datetime = Field(..., example="2025-12-06T08:00:00Z")


# ============================================================
# CUSTOMER REQUEST TO CREATE LOAN
# ============================================================
class LoanApplicationCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., gt=18, lt=100, example=30)
    income: float = Field(..., gt=0, example=50000.0)
    loan_amount: float = Field(..., gt=0, example=150000.0)
    pan: str = Field(..., example="ABCDE1234F")


# ============================================================
# FULL LOAN APPLICATION OUTPUT
# (Used by POST /loan/ and GET /loan/{id})
# ============================================================
class LoanApplicationOut(LoanApplicationCreate):
    application_id: str = Field(..., example="ln_abc123def456")
    status: str = Field(..., example="approved")
    credit_score: int | None = Field(None)
    risk_level: str | None = Field(None)
    decision_reason: str | None = Field(None)
    llm_explanation: str | None = Field(None)
    llm_status_explanation: str | None = Field(None)

    # Manual review fields
    officer_notes: str | None = Field(None)
    reviewed_by: str | None = Field(None)

    created_at: datetime = Field(...)

    history: list[StatusChange] = Field(default_factory=list)


# ============================================================
# LOAN OFFICER MANUAL REVIEW REQUEST
# ============================================================
class ManualReviewRequest(BaseModel):
    action: str = Field(..., example="approve")  # approve / reject
    notes: str = Field(..., example="Everything verified.")
    officer: str = Field(..., example="LoanOfficer")


# ============================================================
# CUSTOMER CHAT REQUEST
# ============================================================
class ChatRequest(BaseModel):
    message: str = Field(..., example="Why is my loan still pending?")
