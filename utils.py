import random


def get_credit_score(pan: str) -> int:
    random.seed(pan)
    return random.randint(550, 820)
