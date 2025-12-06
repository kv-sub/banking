# services.py
from datetime import datetime
import uuid
from agent import run_agent
from db_postgres import (
    check_active_application,
    log_status_change,
)
from llm_service import generate_status_explanation
from db_postgres import get_status_history


def generate_application_data(req, use_llm: bool = False):
    data = req.dict()
    data["application_id"] = f"ln_{uuid.uuid4().hex[:12]}"
    data["created_at"] = datetime.utcnow()

    if check_active_application(data["pan"]):
        raise Exception(f"Active application already exists for PAN {data['pan']}")

    # Status: Submitted
    old_status = None
    new_status = "submitted"
    data["status"] = new_status
    log_status_change(data["application_id"], old_status, new_status)

    # Run agent
    agent_result = run_agent(data, use_llm=use_llm)

    if not agent_result["validation"]["success"]:
        raise Exception(agent_result["decision"]["reason"])

    # Status: Processing
    old_status = new_status
    new_status = "processing"
    log_status_change(data["application_id"], old_status, new_status)

    # Fill results
    data["credit_score"] = agent_result["credit_score"]["credit_score"]
    data["risk_level"] = agent_result["risk"]["risk_level"]
    data["decision_reason"] = agent_result["decision"]["reason"]

    # Final status
    final_status = agent_result["status"]
    data["status"] = final_status

    log_status_change(data["application_id"], new_status, final_status)

    # Add status explanation
    history = get_status_history(data["application_id"])
    data["llm_status_explanation"] = generate_status_explanation(data, history)

    if "llm_explanation" in agent_result:
        data["llm_explanation"] = agent_result["llm_explanation"]

    return data
