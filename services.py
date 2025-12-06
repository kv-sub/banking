# services.py
from datetime import datetime
import uuid

from agent import run_agent
from db_postgres import (
    check_active_application,
    log_status_change,
    get_status_history,
)


def generate_application_data(req):
    data = req.dict()
    data["application_id"] = f"ln_{uuid.uuid4().hex[:12]}"
    data["created_at"] = datetime.utcnow()

    data["llm_explanation"] = None
    data["llm_status_explanation"] = None
    data["officer_notes"] = None
    data["reviewed_by"] = None

    # Check PAN
    if check_active_application(data["pan"]):
        raise Exception(f"Active application already exists for PAN {data['pan']}")

    # submitted
    log_status_change(data["application_id"], None, "submitted")
    data["status"] = "submitted"

    # run agent
    agent_result = run_agent(data)

    # validation failed → reject
    if not agent_result["validation"]["success"]:
        data["status"] = "rejected"
        data["credit_score"] = None
        data["risk_level"] = None
        data["decision_reason"] = agent_result["decision"]["reason"]
        return data

    # processing
    log_status_change(data["application_id"], "submitted", "processing")

    # fill results
    data["credit_score"] = agent_result["credit_score"]["credit_score"]
    data["risk_level"] = agent_result["risk"]["risk_level"]
    data["decision_reason"] = agent_result["decision"]["reason"]

    # manual review route
    if agent_result["status"] == "manual_review":
        log_status_change(data["application_id"], "processing", "manual_review")
        data["status"] = "manual_review"
        return data

    # auto final decision
    data["status"] = agent_result["status"]
    log_status_change(data["application_id"], "processing", data["status"])

    return data
