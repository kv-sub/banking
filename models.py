# models.py
from pydantic import BaseModel, Field
from datetime import datetime

class StatusChange(BaseModel):
    old_status: str | None = Field(None, example=None)
    new_status: str = Field(..., example="processing")
    changed_at: datetime = Field(..., example="2025-12-06T08:00:00Z")

class ManualReviewRequest(BaseModel):
    action: str = Field(..., example="approve")
    notes: str | None = Field(None, example="Reviewed and verified.")
    officer: str = Field(..., example="LoanOfficer")

class LoanApplicationCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., gt=18, lt=100)
    income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    pan: str = Field(..., example="ABCDE1234F")

class LoanApplicationOut(LoanApplicationCreate):
    application_id: str
    status: str
    credit_score: int | None
    risk_level: str | None
    decision_reason: str | None
    llm_explanation: str | None
    llm_status_explanation: str | None
    officer_notes: str | None
    reviewed_by: str | None
    created_at: datetime
    history: list[StatusChange]
