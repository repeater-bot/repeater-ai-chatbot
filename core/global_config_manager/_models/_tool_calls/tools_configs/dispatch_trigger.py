from pydantic import BaseModel

class DispatchTriggerConfig(BaseModel):
    server_base_url: str | None = None