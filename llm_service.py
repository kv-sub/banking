# llm_service.py
import os
import requests
from dotenv import load_dotenv

# Load .env reliably
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

OLLAMA_BASE = os.getenv("OLLAMA_BASE")       # http://localhost:11434
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")     # llama3.2:3b
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate?stream=false"   # full endpoint URL


def generate_llm_explanation(application: dict, agent_result: dict) -> str:
    """
    Calls local Ollama LLM and returns a concise explanation for a loan decision.
    Returns a graceful fallback message if the LLM call fails.
    """

    prompt = f"""
You are an assistant that explains bank loan decisions clearly and concisely for customers.

Application:
Name: {application.get('name')}
Age: {application.get('age')}
Income: {application.get('income')}
Loan Amount: {application.get('loan_amount')}
PAN: {application.get('pan')}

STP results:
Credit score: {agent_result['credit_score']['credit_score']}
Risk level: {agent_result['risk']['risk_level']}
Decision: {"approved" if agent_result['decision']['approved'] else "rejected"}
Reason: {agent_result['decision']['reason']}

Provide:
1) A one-paragraph explanation in plain language for the customer.
2) If rejected or medium/high risk, provide 2 simple suggestions.
Limit to 120–150 words.
"""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False  # important to disable streaming for FastAPI
        }

        # Increase timeout for local LLM inference
        resp = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60  # seconds
        )
        resp.raise_for_status()
        data = resp.json()

        # Standard response format: {"response": "..."}
        if "response" in data:
            return data["response"]

        # Rare formats: {"results": [{"content": "..."}]}
        if "results" in data and isinstance(data["results"], list) and data["results"]:
            r0 = data["results"][0]
            return r0.get("content") or r0.get("text") or ""

        # fallback
        return str(data)

    except Exception as e:
        # Fail gracefully — do not break main flow
        return f"(LLM unavailable: {e})"
