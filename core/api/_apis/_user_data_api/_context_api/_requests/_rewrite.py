from pydantic import BaseModel
from ......user_data_managers.context import ContentUnit

class RewriteContext(BaseModel):
    index: int
    content: ContentUnit