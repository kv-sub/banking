# agent_tools.py
from pydantic import BaseModel
from utils import get_or_update_credit_score

# 1. Validation
class ValidateInputResult(BaseModel):
    success: bool
    message: str

def validate_input_tool(name: str, age: int, income: float, loan_amount: float, pan: str):
    if age < 18 or age > 100:
        return ValidateInputResult(success=False, message="Age out of allowed range").dict()
    if income <= 0:
        return ValidateInputResult(success=False, message="Income must be greater than zero").dict()
    if loan_amount <= 0:
        return ValidateInputResult(success=False, message="Loan amount must be greater than zero").dict()
    if loan_amount > income * 10:
        return ValidateInputResult(success=False, message="Loan amount extremely high relative to income").dict()
    return ValidateInputResult(success=True, message="Input looks valid").dict()

# 2. Credit score
class CreditScoreResult(BaseModel):
    credit_score: int

def credit_score_tool(pan: str, income: float, loan_amount: float):
    score = get_or_update_credit_score(
        pan=pan,
        income=income,
        loan_amount=loan_amount
    )
    return CreditScoreResult(credit_score=score).dict()

# 3. Risk rules
class RiskResult(BaseModel):
    risk_level: str
    reason: str

def risk_rules_tool(income: float, loan_amount: float, credit_score: int):
    if credit_score < 550:
        return RiskResult(risk_level="high", reason="Very low credit score").dict()
    if loan_amount > income * 5:
        return RiskResult(risk_level="high", reason="Loan amount too high relative to income").dict()
    if loan_amount > income * 3:
        return RiskResult(risk_level="medium", reason="Moderate risk loan amount").dict()
    return RiskResult(risk_level="low", reason="Healthy income-to-loan ratio").dict()

# 4. Decision tool
class DecisionResult(BaseModel):
    approved: bool
    reason: str
    manual_review: bool = False  # NEW FLAG

def decision_tool(credit_score: int, risk_level: str):
    # 🚨 Manual review triggers
    if credit_score < 600:
        return DecisionResult(approved=False, manual_review=True,
               reason="Low credit score requires manual verification").dict()

    if risk_level == "high":
        return DecisionResult(approved=False, manual_review=True,
               reason="High-risk profile requires manual review").dict()

    # Auto reject (no manual review)
    if credit_score < 630:
        return DecisionResult(approved=False,
               reason="Credit score below eligibility threshold").dict()

    # Auto reject for high risk
    if risk_level == "high":
        return DecisionResult(approved=False,
               reason="Risk too high for approval").dict()

    # Auto approve
    return DecisionResult(approved=True, reason="Good credit score and acceptable risk").dict()
