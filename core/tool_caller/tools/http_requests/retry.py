from pydantic import BaseModel, Field

class Retry(BaseModel):
    status_codes: list[int] = Field(default_factory=list, description="The HTTP status codes to retry on.")
    retries: int = Field(3, description="The number of retries to attempt.")
    backoff: float = Field(1.0, ge=0.0, description="The backoff time in seconds between retries.")
    jitter: float = Field(0.0, ge=0.0, description="The jitter time in seconds added to the backoff time for each retry.")
