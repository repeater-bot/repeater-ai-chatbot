from pydantic import BaseModel, Field

class StarlarkToolConfig(BaseModel):
    default_max_steps: int = Field(default = 1000)
    default_max_allocs: int = Field(default = 10485760)
    force_max_steps: int = Field(default = 1000)
    force_max_allocs: int = Field(default = 10485760)