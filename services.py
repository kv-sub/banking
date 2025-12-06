# services.py
from datetime import datetime
import uuid
from agent import run_agent
from db_postgres import check_active_application

def generate_application_data(req, use_llm: bool = False):
    """
    Generate all application data using agent orchestration.
    """
    data = req.dict()
    data["application_id"] = f"ln_{uuid.uuid4().hex[:12]}"
    data["created_at"] = datetime.utcnow()

    # 0️⃣ Check for active application for this PAN (prevent spam)
    if check_active_application(data["pan"]):
        raise Exception(f"Active application already exists for PAN {data['pan']}")

    # Temporarily set status to 'submitted' — real status will come from agent
    data["status"] = "submitted"

    # Run agent orchestration (validation -> credit -> risk -> decision)
    agent_result = run_agent(data, use_llm=use_llm)

    # If validation failed, raise (agent_result contains reason)
    if not agent_result["validation"]["success"]:
        raise Exception(agent_result["decision"]["reason"])

    # Map results into data for DB insert
    data["status"] = "processing"  # mark processing while persisting (final status will be set by agent result)
    data["credit_score"] = agent_result["credit_score"]["credit_score"]
    data["risk_level"] = agent_result["risk"]["risk_level"]
    data["decision_reason"] = agent_result["decision"]["reason"]

    # If LLM explanation present, include it
    if "llm_explanation" in agent_result:
        data["llm_explanation"] = agent_result["llm_explanation"]

    # Final status from agent:
    final_status = agent_result["status"]
    data["status"] = final_status

    return data
