from pydantic import BaseModel

class ProgramData(BaseModel):
    variables: str = "" # Implement format resolution in tools.