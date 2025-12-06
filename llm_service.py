import os
import requests
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

OLLAMA_BASE = os.getenv("OLLAMA_BASE")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"


def _stream_ollama(prompt: str) -> str:
    """
    Robust streaming handler for Ollama.
    Works with both streaming and non-streaming models.
    Never fails on partial JSON chunks.
    Never raises timeout issues.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": True},
            stream=True,
            timeout=None  # Critical: allow streaming without timeout
        )

        final_text = []

        for line in response.iter_lines():
            if not line:
                continue

            try:
                obj = json.loads(line.decode("utf-8"))
                if "response" in obj:
                    final_text.append(obj["response"])
            except:
                # Ignore malformed lines safely
                continue

        return "".join(final_text).strip()

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
Credit score: {agent_result['credit_score']['credit_score']}
Risk level: {agent_result['risk']['risk_level']}
Decision: {"approved" if agent_result['decision']['approved'] else "rejected"}
Reason: {agent_result['decision']['reason']}
"""

    return _stream_ollama(prompt)


def generate_status_explanation(application: dict, history: list) -> str:
    timeline = "\n".join(
        [f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}" for h in history]
    )

    prompt = f"""
Explain to the customer how their loan application progressed.

Application ID: {application['application_id']}

Timeline:
{timeline}

Write a short, friendly summary.
"""

    return _stream_ollama(prompt)
