from email import message

import orjson
import traceback

from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar, Any, Generic
from pydantic import BaseModel, ValidationError
from .function import CallMode
from ....user_config_manager import UserConfigs
from ....global_config_manager import GlobalConfigs
from loguru import logger

T = TypeVar("T")

class ToolCallPacakage(ABC, Generic[T]):
    """
    Abstract class for tool calling package
    """
    class Params(BaseModel):
        pass

    class Result(BaseModel):
        pass

    name: ClassVar[str] = ""
    """The name of the tool"""

    enabled: ClassVar[bool] = True
    """Enable the tool"""

    description: ClassVar[str] = ""
    """The document of the tool"""

    force_choice: ClassVar[bool] = False
    """Force choice the tool"""

    json_result: ClassVar[bool] = False
    """Whether the result is json"""

    call_mode: ClassVar[CallMode] = CallMode.SYNC
    """The call mode of the tool"""

    def __init__(self, user_id: str, user_configs: UserConfigs, global_configs: GlobalConfigs, *args, **kwargs):
        self.user_id = user_id
        self.user_configs = user_configs
        self.global_configs = global_configs
        self.extra_positional_args = args
        self.extra_keyword_args = kwargs
        self.__post_init__()
    
    def __post_init__(self):
        pass

    def get_description(self) -> str:
        """
        Override the method to customize more complex description rules.
        """
        return self.description or self.__doc__ or ""

    @abstractmethod
    def call(self, args: Params) -> T:
        pass

    async def on_error(self, error: Exception) -> T | Any | None:
        """
        This method is called when an error occurs during the execution of the tool.
        """
        logger.exception(
            "Could not call tool {name}: {error}",
            name = self.name,
            error = error
        )
        message = f"Could not call tool {self.name}: {error}"
        return message
    
    async def on_args_validation_error(self, error: ValidationError) -> T | Any | None:
        errors = error.errors()
        buffer: list[str] = []
        for now_error in errors:
            buffer.append(f"{'.'.join(str(i) for i in now_error['loc'])}: {now_error['msg']}")
        error_message = "\n".join(buffer)
        return f"Tool Args Validation Error for {self.name}:\n{error_message}"

    async def on_args_json_decode_error(self, error: orjson.JSONDecodeError) -> T | Any | None:
        return f"Invalid JSON: {error.msg}"

    async def on_result_json_encode_error(self, error: orjson.JSONEncodeError) -> T | Any | None:
        return f"Tool Result JSON Encode Error for {self.name}: {error}"
    
    async def on_json_result_string_encode_error(self, data: bytes, error: UnicodeEncodeError) -> T | Any | None:
        return f"Tool Result JSON Can't be encoded to utf-8 string for {self.name}: {error}"