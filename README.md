# Loan STP - Day 1 (Prototype)
This is the Day 1 starter for the 4-day learning project: a minimal FastAPI app that accepts loan applications,
stores them in SQLite, and returns a mock credit score. The goal today is to have a working ingestion endpoint
and a simple data store.

## Files
- main.py: FastAPI application with /loan/apply and /loan/{id} endpoints
- db.py: SQLite helper (loan_stp.db created in the project folder)
- models.py: Pydantic models for request/response
- utils.py: mock credit score generator
- requirements.txt: python deps

## Run locally (recommended)
1. Create a virtualenv: `python -m venv venv && source venv/bin/activate`
2. Install deps: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. POST a JSON to http://localhost:8000/loan/apply (use Postman or curl)
   sample:
{
  "name": "John",
  "age": 28,
  "income": 45000,
  "loan_amount": 200000,
  "pan": "ABCDE1234F"
}

## What we built today
- Ingestion endpoint for loan applications
- SQLite storage
- Mock credit score calculation
- Retrieval endpoint to check status
