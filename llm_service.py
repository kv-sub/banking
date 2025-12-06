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


def _parse_stream(text: str) -> str:
    """Handles both streaming and non-streaming JSON safely."""
    lines = text.strip().split("\n")
    out = []
    for line in lines:
        try:
            obj = json.loads(line)
            if "response" in obj:
                out.append(obj["response"])
        except:
            continue
    return "".join(out).strip()


def ask_llm(prompt: str) -> str:
    """Non-blocking request to Ollama, no timeout."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
            stream=True,
            timeout=None
        )
        final = []
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                j = json.loads(line.decode())
                if "response" in j:
                    final.append(j["response"])
            except:
                continue
        return "".join(final).strip()

    except Exception as e:
        return f"(LLM unavailable: {e})"


def generate_llm_explanation(application: dict, agent_result: dict) -> str:
    prompt = f"""
Explain this loan decision clearly:

Applicant:
Name: {application.get('name')}
Age: {application.get('age')}
Income: {application.get('income')}
Loan Amount: {application.get('loan_amount')}

Results:
Credit score: {agent_result['credit_score']}
Risk level: {agent_result['risk_level']}
Decision: {application['status']}
Reason: {application['decision_reason']}
"""
    return ask_llm(prompt)


def generate_status_explanation(application: dict, history: list) -> str:
    timeline = "\n".join(
        f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}"
        for h in history
    )
    prompt = f"""
Explain this loan application's status timeline:

Application ID: {application['application_id']}

Timeline:
{timeline}

Provide a simple, friendly summary.
"""
    return ask_llm(prompt)


def generate_full_explanation(application: dict, agent_result: dict, history: list):
    """Used by new API endpoint."""
    return {
        "llm_explanation": generate_llm_explanation(application, agent_result),
        "llm_status_explanation": generate_status_explanation(application, history)
    }
