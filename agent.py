from agent_tools import (
    validate_input_tool,
    credit_score_tool,
    risk_rules_tool,
    decision_tool
)

def run_agent(application: dict, use_llm: bool = False):
    result = {}

    # 1. Validation
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
        result["decision"] = {"approved": False, "reason": "Validation failed"}
        return result

    # 2. Credit Score
    credit_score = credit_score_tool(application["pan"])
    result["credit_score"] = credit_score

    # 3. Risk
    risk = risk_rules_tool(
        income=application["income"],
        loan_amount=application["loan_amount"],
        credit_score=credit_score["credit_score"]
    )
    result["risk"] = risk

    # 4. Decision
    decision = decision_tool(
        credit_score=credit_score["credit_score"],
        risk_level=risk["risk_level"]
    )
    result["decision"] = decision

    # Optional: add LLM explanation (for demo)
    if use_llm:
        result["llm_explanation"] = "This is where LLM reasoning would go."

    return result
