from pydantic import BaseModel

class RefreshResponse(BaseModel):
    message: str = "Model info refreshed successfully"
    status: str = "ok"