from pydantic import BaseModel, ConfigDict, Field
from ._ping_provider import PingProvider

class ModelAPIConfig(BaseModel):
    base_url: str = ""
    timeout: int | float | None = 10.0
    api_key_env_name: str = "MODEL_INFO_API_KEY"
    default_model_id: str | list[str] = "chat"
    default_image_model_id: str | list[str] = ""
    default_embedding_model_id: str | list[str] = ""
    ping_provider: PingProvider = PingProvider()
    random_decay_index: float = Field(default=0.5, ge=0.0, le=1.0)