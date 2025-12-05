from fastapi import FastAPI, HTTPException
from models import LoanApplicationCreate, LoanApplicationOut
from services import generate_application_data
from db_postgres import init_db, insert_application, get_application

app = FastAPI(title="Bank Loan STP API")

init_db()

@app.post("/loan/", response_model=LoanApplicationOut)
def create_loan_application(request: LoanApplicationCreate):
    try:
        data = generate_application_data(request)
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
