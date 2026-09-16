import numpy as np

def calculate_skewness(data):
    n = len(data)
    if n < 3:
        return np.nan
    
    mean = np.mean(data)
    m2 = np.sum((data - mean) ** 2) / n
    m3 = np.sum((data - mean) ** 3) / n
    
    if m2 == 0:
        return np.nan
    
    g1 = m3 / (m2 ** 1.5)
    correction = np.sqrt(n * (n - 1)) / (n - 2)
    return g1 * correction