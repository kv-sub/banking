# main.py
from fastapi import FastAPI, HTTPException, Query
import os
from models import LoanApplicationCreate, LoanApplicationOut
from services import generate_application_data
from db_postgres import init_db, insert_application, get_application
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


app = FastAPI(title="Bank Loan STP API")

init_db()

@app.post("/loan/", response_model=LoanApplicationOut)
def create_loan_application(request: LoanApplicationCreate, use_llm: bool = Query(False)):
    """
    Create a new loan application.
    Pass ?use_llm=true to enable LLM explanation (Ollama must be running).
    """
    try:
        data = generate_application_data(request, use_llm=use_llm)
        insert_application(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return LoanApplicationOut(**data)

@app.get("/loan/{application_id}", response_model=LoanApplicationOut)
def get_application_status(application_id: str):
    record = get_application(application_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    return LoanApplicationOut(**record)
