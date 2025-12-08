# llm_service.py (Groq-powered)
import os
from groq import Groq
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# ============================================================
# GROQ LLM CALL
# ============================================================
def _generate(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )

        # FOR YOUR SDK → message.content is an attribute, not a dict
        content = response.choices[0].message.content

        return content.strip() if isinstance(content, str) else str(content)

    except Exception as e:
        print("🔥 LLM ERROR:", e)
        return f"(LLM unavailable: {e})"



# ============================================================
# OLD FUNCTION (still used by agent)
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
    return _generate(prompt)


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
    return _generate(prompt)


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

    return {"llm_explanation": _generate(prompt)}


# ============================================================
# CUSTOMER CHAT
# ============================================================
def generate_chat_response(app, history, message):
    timeline = "".join(
        f"- {h['old_status']} → {h['new_status']} at {h['changed_at']}\n"
        for h in history
    )

    prompt = f"""
You are a helpful loan assistant AI.

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

Respond politely and clearly.
"""

    return {"response": _generate(prompt)}
