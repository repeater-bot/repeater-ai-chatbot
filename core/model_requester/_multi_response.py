from typing import Generator
from ..request_log import RequestLog
from ..call_api.completions_api import Request, Response
from ..user_data_managers.context import Context, ContentUnit
from pydantic import BaseModel, Field

class MultiResponse(BaseModel):
    historical_context: Context = Field(default_factory=Context)
    responses: list[Response] = Field(default_factory=list)
    tool_requests: list[list[ContentUnit]] = Field(default_factory=list)

    def __getitem__(self, key: int | slice) -> Response:
        if isinstance(key, int | slice):
            return self.responses[key]
        else:
            raise TypeError("Invalid key type")

    def add(self, response: Response):
        self.responses.append(response)
    
    def add_copy(self, response: Response):
        response_copy = response.model_copy()
        response_copy.historical_context = response.historical_context.copy()
        response_copy.new_context = response.new_context.copy()
        self.add(response_copy)

    def new_contexts(self):
        context = Context()
        for index, response in enumerate(self.responses):
            context.extend(response.new_context)
            if index < len(self.tool_requests):
                context.extend(self.tool_requests[index])
        return context
    
    def request_logs(self) -> list[RequestLog]:
        return [response.request_log for response in self.responses]
    
    def __iter__(self) -> Generator[Response, None, None]:
        for response in self.responses:
            yield response