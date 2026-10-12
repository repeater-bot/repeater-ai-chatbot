from pydantic import BaseModel, ConfigDict, Field
from ....user_data_managers.context import Context
from ....request_log import RequestLog, TimeStamp, Logprob
from ._tokens_count import TokensCount
from ._finish_reason import FinishReason
from ._tool_calls import ToolCall

class Response(BaseModel):
    """
    This class is used to store the response data
    """
    model_config = ConfigDict(
        validate_assignment=True
    )

    id: str = ""
    user_id: str = ""

    historical_context: Context = Field(default_factory=Context)
    new_context: Context = Field(default_factory=Context)
    
    model: str = ""
    created: int = 0
    token_usage: TokensCount | None = None
    stream: bool = False
    tool_calls: list[ToolCall] | None = None
    finish_reason: FinishReason | str = FinishReason.STOP
    system_fingerprint: str | None = None
    logprobs: list[Logprob] | None = None

    stream_processing_start_time_ns:TimeStamp = Field(default_factory=TimeStamp)
    stream_processing_end_time_ns:TimeStamp = Field(default_factory=TimeStamp)
    chunk_times: list[TimeStamp] = Field(default_factory=list)
    request_log: RequestLog = Field(default_factory=RequestLog)

    @property
    def finish_reason_cause(self) -> str:
        match self.finish_reason:
            case FinishReason.STOP:
                reason = "Reached STOP list or natural stopping point."
            case FinishReason.LENGTH:
                reason = "Exceeded maximum output length limit."
            case FinishReason.CONTENT_FILTER:
                reason = "Content triggered filtering policy."
            case FinishReason.TOOL_CALLS:
                reason = "Output contains tool calls."
            case FinishReason.INSUFFICIENT_SYSTEM_RESOURCE:
                reason = "Insufficient system resource to complete the request."
            case finish_reason:
                reason = f"Unknown finish reason: {finish_reason}"
        return reason
