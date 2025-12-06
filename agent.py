# agent.py
from agent_tools import (
    validate_input_tool,
    credit_score_tool,
    risk_rules_tool,
    decision_tool
)
from llm_service import generate_llm_explanation

def run_agent(application: dict, use_llm: bool = False):
    """
    Runs validation → credit score → risk rules → decision.
    Now supports MANUAL REVIEW.
    """

    result = {}

    # 1️⃣ Validation
    validation = validate_input_tool(
        name=application["name"],
        age=application["age"],
        income=application["income"],
        loan_amount=application["loan_amount"],
        pan=application["pan"]
    )
    result["validation"] = validation

    if not validation["success"]:
        result["status"] = "rejected"
        result["credit_score"] = None
        result["risk"] = None
        result["decision"] = {"approved": False, "reason": validation["message"]}
        return result

    # 2️⃣ Credit Score
    credit_score = credit_score_tool(application["pan"])
    result["credit_score"] = credit_score

    # 3️⃣ Risk Assessment
    risk = risk_rules_tool(
        income=application["income"],
        loan_amount=application["loan_amount"],
        credit_score=credit_score["credit_score"],
    )
    result["risk"] = risk

    # 4️⃣ Decision
    decision = decision_tool(
        credit_score=credit_score["credit_score"],
        risk_level=risk["risk_level"],
    )
    result["decision"] = decision

    # 5️⃣ Status determination
    if decision.get("manual_review"):
        result["status"] = "manual_review"
    else:
        result["status"] = "approved" if decision["approved"] else "rejected"

    # 6️⃣ LLM explanation (optional)
    if use_llm:
        result["llm_explanation"] = generate_llm_explanation(application, result)

    return result
