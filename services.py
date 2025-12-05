from datetime import datetime
import uuid
from agent_tools import validate_input_tool, credit_score_tool, risk_rules_tool, decision_tool

def generate_application_data(req):
    data = req.dict()
    data["application_id"] = f"ln_{uuid.uuid4().hex[:12]}"
    data["status"] = "submitted"

    # 1️⃣ Validate input — pass only required fields
    validation = validate_input_tool(
        name=data['name'],
        age=data['age'],
        income=data['income'],
        loan_amount=data['loan_amount'],
        pan=data['pan']
    )
    if not validation['success']:
        raise Exception(validation['message'])

    # 2️⃣ Credit score
    credit_score = credit_score_tool(data['pan'])
    data['credit_score'] = credit_score['credit_score']

    # 3️⃣ Risk assessment
    risk = risk_rules_tool(data['income'], data['loan_amount'], data['credit_score'])
    data['risk_level'] = risk['risk_level']

    # 4️⃣ Decision
    decision = decision_tool(data['credit_score'], data['risk_level'])
    data['decision_reason'] = decision['reason']

    data['created_at'] = datetime.utcnow()
    return data
