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
    Orchestrator for STP loan application.
    Executes all tools in order and returns full result.
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
        result["credit_score"] = None
        result["risk"] = None
        result["decision"] = {"approved": False, "reason": validation["message"]}
        result["status"] = "rejected"
        return result

    # 2️⃣ Credit Score
    credit_score = credit_score_tool(application["pan"])
    result["credit_score"] = credit_score

    # 3️⃣ Risk Assessment
    risk = risk_rules_tool(
        income=application["income"],
        loan_amount=application["loan_amount"],
        credit_score=credit_score["credit_score"]
    )
    result["risk"] = risk

    # 4️⃣ Decision
    decision = decision_tool(
        credit_score=credit_score["credit_score"],
        risk_level=risk["risk_level"]
    )
    result["decision"] = decision

    # 5️⃣ Determine application status
    result["status"] = "approved" if decision["approved"] else "rejected"

    # 6️⃣ Optional LLM explanation
    if use_llm:
        result["llm_explanation"] = generate_llm_explanation(application, result)

    return result
