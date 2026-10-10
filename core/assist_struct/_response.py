from pydantic import BaseModel, ConfigDict
from ..user_data_managers.context import ContentBlock, Context
from ..request_log import RequestLog

class Response(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True
    )

    context: Context | None = None
    user_raw_input: str | None = None
    user_input: str | list[ContentBlock] | None = None
    model_group: str | None = None
    model_name: str | None = None
    model_uid: str | None = None
    create_time: int | None = None
    id: str | None = None
    finish_reason_cause: str | None = None
    finish_reason_code: str | None = None
    request_log: list[RequestLog] | None = None
    request_statistics: str | None = None
    status: int = 200