from pydantic import BaseModel, Field

class LoanApplicationIn(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., ge=18, le=100, example=30)
    income: float = Field(..., gt=0, example=45000)
    loan_amount: float = Field(..., gt=0, example=200000)
    pan: str = Field(..., min_length=10, max_length=10, example="ABCDE1234F")

class LoanApplicationOut(BaseModel):
    application_id: str
    name: str
    age: int
    income: float
    loan_amount: float
    pan: str
    status: str
    credit_score: int
    created_at: str
