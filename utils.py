import random

# Very simple mock credit score function for Day 1 prototype.
# In later days we'll replace this with a better mock service or ML model.
def get_credit_score(pan: str) -> int:
    random.seed(pan)  # deterministic per PAN for repeatability
    # return a score between 550 and 820
    return random.randint(550, 820)
