# llm_service.py
import os
import requests
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

OLLAMA_BASE = os.getenv("OLLAMA_BASE")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"


# ============================================================
# INTERNAL STREAM HANDLER
# ============================================================
def _stream_ollama(prompt: str) -> str:
    """
    Safe streaming function for Ollama.
    Handles malformed chunks, partial JSON, or non-streaming fallback.
    """
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
            stream=True,
            timeout=None,
        )

        collected = []

        for line in resp.iter_lines():
            if not line:
                continue

            try:
                obj = json.loads(line.decode("utf-8"))
                if "response" in obj:
                    collected.append(obj["response"])
            except:
                continue

        return "".join(collected).strip()

    except Exception as e:
        return f"(LLM unavailable: {e})"


# ============================================================
# OLD FUNCTION (still used by initial agent)
# ============================================================
def generate_llm_explanation(application: dict, agent_result: dict) -> str:
    prompt = f"""
Explain this loan decision clearly:

Applicant:
Name: {application.get('name')}
Age: {application.get('age')}
Income: {application.get('income')}
Loan Amount: {application.get('loan_amount')}

Results:
Credit score: {agent_result['credit_score']['credit_score']}
Risk level: {agent_result['risk']['risk_level']}
Decision: {"approved" if agent_result['decision']['approved'] else "rejected"}
Reason: {agent_result['decision']['reason']}
"""
    return _stream_ollama(prompt)


# ============================================================
# STATUS EXPLANATION
# ============================================================
def generate_status_explanation(application: dict, history: list) -> str:
    timeline = "\n".join(
        f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}"
        for h in history
    )

    prompt = f"""
Explain this loan application's processing timeline.

Application ID: {application['application_id']}

Timeline:
{timeline}

Write a short, friendly explanation for the customer.
"""
    return _stream_ollama(prompt)


# ============================================================
# FULL APPLICATION EXPLANATION (for /explain)
# ============================================================
def generate_full_explanation(app, agent_data, history):
    timeline = "".join(
        f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}\n"
        for h in history
    )

    prompt = f"""
Provide a detailed explanation of this loan application:

Applicant: {app['name']}
Age: {app['age']}
Income: {app['income']}
Loan Amount: {app['loan_amount']}
PAN: {app['pan']}

Internal Calculations:
- Credit Score: {agent_data['credit_score']}
- Risk Level: {agent_data['risk_level']}
- Decision Reason: {agent_data['decision_reason']}

Final Status: {app['status']}

Timeline:
{timeline}

Write a clear and structured explanation suitable for the customer.
"""

    return {"llm_explanation": _stream_ollama(prompt)}


# ============================================================
# CHAT WITH CUSTOMER ABOUT THEIR LOAN
# ============================================================
def generate_chat_response(app, history, message):
    timeline = "".join(
        f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}\n"
        for h in history
    )

    prompt = f"""
You are a helpful loan assistant AI. Answer the customer's question politely.

Customer question:
"{message}"

Application details:
- Name: {app['name']}
- Age: {app['age']}
- Income: {app['income']}
- Loan Amount: {app['loan_amount']}
- Current Status: {app['status']}
- Credit Score: {app['credit_score']}
- Risk Level: {app['risk_level']}
- Decision Reason: {app['decision_reason']}

Full Timeline:
{timeline}

Respond clearly and supportively.
"""
    return {"response": _stream_ollama(prompt)}
