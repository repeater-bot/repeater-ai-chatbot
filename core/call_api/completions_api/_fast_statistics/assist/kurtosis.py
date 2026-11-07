import numpy as np


def calculate_kurtosis(data: np.ndarray[tuple[int]]):
    
    n = len(data)
    if n < 4:
        return np.nan
    mean = np.mean(data)
    variance = np.var(data)
    if variance == 0 or not np.isfinite(variance):
        return np.nan          # 常量序列峰度无定义（0/0），与 skewness 保持一致
    return np.sum((data - mean) ** 4) / (n * variance ** 2) - 3