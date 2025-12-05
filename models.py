from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class LoanApplicationCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., gt=18, lt=100, example=30)
    income: float = Field(..., gt=0, example=45000.0)
    loan_amount: float = Field(..., gt=0, example=200000.0)
    pan: str = Field(..., example="ABCDE1234F")

    @validator("pan")
    def validate_pan(cls, v):
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if not re.match(pattern, v.upper()):
            raise ValueError("Invalid PAN format")
        return v.upper()


class LoanApplicationOut(LoanApplicationCreate):
    application_id: str
    status: str
    credit_score: int | None
    risk_level: str | None
    decision_reason: str
    created_at: datetime
