import random

def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    if attempt < 0:
        raise ValueError("Attempt must be greater than 0")
    return base_delay * (2 ** attempt)

def exponential_backoff_with_jitter(attempt: int, base_delay: float = 1.0, with_jitter: float = 0.0) -> float:
    delay = exponential_backoff(attempt, base_delay)

    if with_jitter > 0:
        delay += random.uniform(0, with_jitter)
    elif with_jitter == 0:
        return delay
    else:
        raise ValueError("with_jitter must be greater than 0")
    return delay
