from pydantic import BaseModel
from .._content_block import ContentBlock

class ContentResult(BaseModel):
    """When this type is used as the return value, it is resolved to a custom message segment."""
    content: str | list[ContentBlock]