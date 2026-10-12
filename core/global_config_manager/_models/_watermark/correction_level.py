from enum import StrEnum

class WatermarkCorrectionLevel(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    QUARTILE = "quartile"
    HIGH = "high"