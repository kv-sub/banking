# utils.py
import random

def get_credit_score(pan: str) -> int:
    """
    Deterministic (per PAN) credit score for demo reproducibility.
    Keep as deterministic so same PAN -> same score (demo-friendly).
    """
    random.seed(pan)
    return random.randint(550, 820)
