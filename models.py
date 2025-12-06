# models.py
from pydantic import BaseModel, Field
from datetime import datetime


class StatusChange(BaseModel):
    old_status: str | None = Field(None, example=None)
    new_status: str = Field(..., example="processing")
    changed_at: datetime = Field(..., example="2025-12-06T08:00:00Z")


class LoanApplicationCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., gt=18, lt=100, example=30)
    income: float = Field(..., gt=0, example=45000.0)
    loan_amount: float = Field(..., gt=0, example=200000.0)
    pan: str = Field(..., example="ABCDE1234F")


class LoanApplicationOut(LoanApplicationCreate):
    application_id: str = Field(..., example="ln_abc123def456")
    status: str = Field(..., example="approved")
    credit_score: int | None = Field(None, example=720)
    risk_level: str | None = Field(None, example="medium")
    decision_reason: str | None = Field(None, example="Good credit score and acceptable risk")
    llm_explanation: str | None = Field(None, example="Your loan was approved because …")
    llm_status_explanation: str | None = Field(None, example="Your application moved from submitted → processing → approved …")
    created_at: datetime = Field(..., example="2025-12-06T07:56:56.604201Z")
    history: list[StatusChange] = Field(
        default_factory=list,
        example=[
            {"old_status": None, "new_status": "submitted", "changed_at": "2025-12-06T07:56:56Z"},
            {"old_status": "submitted", "new_status": "processing", "changed_at": "2025-12-06T07:57:00Z"},
            {"old_status": "processing", "new_status": "approved", "changed_at": "2025-12-06T07:57:04Z"}
        ]
    )
