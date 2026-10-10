from __future__ import annotations

import asyncio
import inspect
import textwrap

from abc import (
    ABC,
    abstractmethod
)
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    NoReturn,
)

import orjson
from loguru import logger
from pydantic import BaseModel, ValidationError

from ....auxiliary.text import text_content_cutter
from ....auxiliary.type_checker import is_iterable
from ....context import (
    CallMode,
    ContentBlock,
    FunctionStruct,
    ToolStruct,
    ToolTypes,
)
from ....global_config_manager import ConfigManager
from ..content_result import ContentResult
from ..exceptions import (
    ToolArgsError,
    ToolContextError,
)
from ..tool_context import (
    ToolContext,
    require_context,
)
from ..typings import (
    New
)
from .params_package import ParamsPackage

if TYPE_CHECKING:
    from fastapi import Request as FastAPI_Request

    from ....global_config_manager import GlobalConfigs
    from ....user_config_manager import UserConfigs


class ToolPackage(ABC):
    """
    Tool Package Base Class

    A tool package is a process wide singleton: it is created once at
    registration time and shared by every user and every request. Anything that
    belongs to a single call is reached through the properties below
    (`user_id`, `user_configs`, `fastapi_request`), which read the context the
    framework set up for the current tool call.
    """

    __time_for_created__: int
    """Time for created"""

    __time_for_created_monotonic__: int
    """Time for created (monotonic)"""

    __time_for_registered__: int
    """Time for registered"""

    __time_for_registered_monotonic__: int
    """Time for registered (monotonic)"""

    __raw_new__: New
    """raw `__new__` method"""

    root: str = "Repeater"
    """The root the tool package belongs to"""

    package_type: str = "Default"
    """Package Type"""

    name: str | None = None
    """Name of the tool package, as the model sees it"""

    enabled: bool = True
    """Whether the tool is registered at all."""

    description: str | Iterable[str] | None = None
    """This handler's description"""

    docs_delimiter: str = "\n"
    """Documentation delimiter"""

    force_choice: bool = False
    """Whether this tool is the one forced by `ToolChoice.FORCE`."""

    json_result: bool = False
    """Whether a non-model result is encoded to JSON explicitly."""

    call_mode: CallMode = CallMode.SYNC
    """
    How `call` is invoked.

    `CallMode.SYNC_IN_THREAD` runs it in a worker thread. `CallMode.SYNC` and
    `CallMode.ASYNC` both work for a sync and an async `call` alike, the
    framework awaits the result whenever it is awaitable.
    """

    class Params(BaseModel):
        """Tool parameters"""
        pass

    class Result(BaseModel):
        """Tool result"""
        pass

    @property
    def package_name(self) -> str:
        """The human-readable name of the Handler (required) """
        return self.name or f"{self.root}.{self.package_type}.{self.__class__.__name__}"

    @classmethod
    def package_path(cls) -> str:
        """The path of the Handler (required) """
        return f"{cls.__module__}.{cls.__qualname__}"

    # ------------------------------------------------------------------ #
    # Per call context
    # ------------------------------------------------------------------ #

    @property
    def context(self) -> ToolContext:
        """The context of the current tool call."""
        return require_context()

    @property
    def user_id(self) -> str:
        """The user that the current tool call belongs to."""
        return self.context.user_id

    @property
    def has_user_configs(self) -> bool:
        """Whether the current tool call carries the configs of its user."""
        return self.context.user_configs is not None

    @property
    def user_configs(self) -> UserConfigs:
        """
        The configs of the user of the current tool call.

        :raises ToolContextError: If the caller did not provide them.
        """
        configs = self.context.user_configs
        if configs is None:
            raise ToolContextError(
                f"Tool {self.package_name} needs the user configs, but the caller did not provide them."
            )
        return configs

    @property
    def fastapi_request(self) -> FastAPI_Request | None:
        """The request that started the generation loop, if there is one."""
        return self.context.fastapi_request

    @property
    def global_configs(self) -> GlobalConfigs:
        """The global configs."""
        return ConfigManager.get_configs()

    async def load_user_configs(self) -> UserConfigs:
        """
        Get the user configs of the current tool call, loading them when the caller did not provide them.

        :return: The user configs.
        """
        context = self.context
        if context.user_configs is None:
            from ....runtime_container import RuntimeContainer

            runtime = RuntimeContainer.get_runtime()
            context.user_configs = await runtime.user_config_manager.load(
                user_id = context.user_id
            )
        return context.user_configs

    # ------------------------------------------------------------------ #
    # Documentation
    # ------------------------------------------------------------------ #

    @classmethod
    def documents(cls) -> str | Iterable[str] | None:
        """This handler's documentation"""
        pass

    def instance_docs(self) -> str | Iterable[str] | None:
        """This handler's instance documentation"""
        pass

    def get_description(self) -> str:
        """Handler description"""

        doc = self.description
        if doc is None:
            doc = self.documents()
        if doc is None:
            doc = self.instance_docs()
        if doc is None:
            doc = self.__doc__
        if doc is None:
            doc = ""

        if isinstance(doc, str):
            return doc
        elif is_iterable(doc):
            merged_doc = self.docs_delimiter.join(doc)
            return merged_doc
        else:
            logger.warning(
                "Tool {package_name} has an invalid documentation type: {doc_type}",
                package_name = self.package_name,
                doc_type=type(doc).__name__,
            )
            return ""

    # ------------------------------------------------------------------ #
    # Model facing schema
    # ------------------------------------------------------------------ #

    @classmethod
    def function_parameters(cls) -> dict[str, Any] | None:
        """
        The JSON schema of this tool's parameters.

        :return: The schema, or None when the tool takes no argument.
        """
        if not cls.Params.model_fields:
            return None
        return cls.Params.model_json_schema()

    def struct(self, strict: bool = False) -> ToolStruct:
        """
        The tool declaration as the model API expects it.

        :param strict: Whether the API should enforce the schema strictly.
        :return: The tool declaration.
        """
        return ToolStruct(
            type = ToolTypes.FUNCTION,
            function = FunctionStruct(
                name = self.package_name,
                description = textwrap.dedent(
                    self.get_description().expandtabs(tabsize = 4)
                ),
                parameters = self.function_parameters(),
                strict = strict,
            )
        )

    # ------------------------------------------------------------------ #
    # Arguments
    # ------------------------------------------------------------------ #

    async def parse_args(self, raw_arguments: str | None) -> Params:
        """
        Decode and validate the raw arguments of a tool call.

        :param raw_arguments: The arguments as the model sent them.
        :return: The parsed arguments.
        :raises ToolArgsError: If they can not be decoded or validated. The message
            of the error is already fit to be sent back to the model.
        """
        params_class = self.Params

        if not params_class.model_fields or raw_arguments is None or raw_arguments.strip() == "":
            data: Any = {}
        else:
            try:
                data = orjson.loads(raw_arguments)
            except orjson.JSONDecodeError as error:
                raise ToolArgsError(
                    str(await self.on_args_json_decode_error(error))
                ) from error

        if not isinstance(data, dict):
            raise ToolArgsError(
                f"Tool Args Validation Error for {self.package_name}:\narguments must be a JSON object"
            )

        try:
            return params_class(**data)
        except ValidationError as error:
            raise ToolArgsError(
                str(await self.on_args_validation_error(error))
            ) from error

    async def on_args_json_decode_error(self, error: orjson.JSONDecodeError) -> Any:
        """
        Build the response for arguments that are not valid JSON.

        :param error: The decode error.
        :return: The content of the tool response.
        """
        return f"Invalid JSON: {error.msg}"

    async def on_args_validation_error(self, error: ValidationError) -> Any:
        """
        Build the response for arguments that do not match the schema of the tool.

        :param error: The validation error.
        :return: The content of the tool response.
        """
        buffer: list[str] = []
        for now_error in error.errors():
            buffer.append(f"{'.'.join(str(i) for i in now_error['loc'])}: {now_error['msg']}")
        error_message = "\n".join(buffer)
        return f"Tool Args Validation Error for {self.package_name}:\n{error_message}"

    async def on_result_json_encode_error(self, error: orjson.JSONEncodeError) -> Any:
        """
        Build the response for a result that can not be encoded to JSON.

        :param error: The encode error.
        :return: The content of the tool response.
        """
        return f"Tool Result JSON Encode Error for {self.package_name}: {error}"

    async def on_json_result_string_encode_error(self, data: bytes, error: UnicodeEncodeError) -> Any:
        """
        Build the response for a JSON result that can not be decoded to an utf-8 string.

        :param data: The encoded result.
        :param error: The decode error.
        :return: The content of the tool response.
        """
        return f"Tool Result JSON Can't be encoded to utf-8 string for {self.package_name}: {error}"

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def __init__(self):
        """
        Initialize the tool package.
        """
        pass

    def __pre_init__(self):
        """
        This method will be called before initialization.
        """
        if isinstance(self.description, str):
            self.description = textwrap.dedent(
                self.description.expandtabs(4)
            )

    def __post_init__(self):
        """
        This method will be called after registration is complete.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #

    async def enter_handler(self, args: ParamsPackage[Params]) -> int:
        """
        This method is called before the handler method.

        :param args: Parameters for the tool.
        :return: The result of the handler method.
        """
        return await self.handler(args)

    async def handler(self, args: ParamsPackage[Params]) -> int:
        """
        Override this method to take over the whole business logic, including
        producing the tool response.

        The default implementation calls `call`, serializes its result and
        pushes it into `args.output`.

        :param args: Parameters for the tool.
        :return: The return code of the tool.
        """
        raw_result = await self._invoke(args.args)
        result = await self._serialize_result(raw_result)

        logger.info(
            "Tool {name}(user: {user_id}) result:\n{result}(length: {length})",
            user_id = args.user_id,
            name = self.package_name,
            result = text_content_cutter(
                str(result),
                self.global_configs.tool_calls.result_max_length_for_logs
            ),
            length = len(result)
        )

        await args.output.put(result)
        return 0

    async def _invoke(self, args: Params) -> Any:
        """
        Call the tool implementation, honoring its call mode.

        :param args: Parameters for the tool.
        :return: Whatever the tool returned.
        """
        if self.call_mode is CallMode.SYNC_IN_THREAD and not inspect.iscoroutinefunction(self.call):
            result = await asyncio.to_thread(self.call, args)
        else:
            result = self.call(args)

        if inspect.isawaitable(result):
            result = await result
        return result

    async def _serialize_result(self, raw_result: Any) -> str | list[ContentBlock]:
        """
        Turn the return value of a tool into the content of a tool response.

        :param raw_result: Whatever the tool returned.
        :return: The content of the tool response.
        """
        if isinstance(raw_result, str):
            return raw_result
        elif isinstance(raw_result, ContentResult):
            return raw_result.content
        elif isinstance(raw_result, BaseModel):
            return orjson.dumps(raw_result.model_dump()).decode("utf-8")

        if self.json_result:
            try:
                bin_result = orjson.dumps(raw_result)
            except orjson.JSONEncodeError as error:
                return str(await self.on_result_json_encode_error(error))

            try:
                return bin_result.decode("utf-8")
            except UnicodeEncodeError as error:
                return str(
                    await self.on_json_result_string_encode_error(bin_result, error)
                )

        try:
            return orjson.dumps(raw_result).decode("utf-8")
        except (orjson.JSONEncodeError, UnicodeEncodeError, TypeError):
            return str(raw_result)

    @abstractmethod
    async def call(self, args: Params) -> Any:
        """
        Override this method to begin writing your business logic.

        :param args: Parameters for the tool.
        :return: The result of the tool.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Error handling
    # ------------------------------------------------------------------ #

    async def on_error(self, exception: Exception, args: ParamsPackage[Params]) -> int | None | NoReturn:
        """
        The error Handler for the Handler.

        It catches all exceptions raised by `handler` by default and pushes a
        message into the output, so the model always sees why a tool failed.

        Includes all the necessary parts for the framework to work

        So you need to determine them and re-throw them to make sure the framework is working properly

        :param exception: The exception
        :param args: Parameters for the tool.
        :return: The result of the tool.
        :raises: The exception
        """
        logger.exception(
            "Could not call tool {name}: {error}",
            name = self.package_name,
            error = exception
        )
        await args.output.put(
            f"Could not call tool {self.package_name}: {exception}"
        )
        return -1

    async def on_interpreter_error(self, exception: BaseException, args: ParamsPackage[Params]) -> int | None | NoReturn:
        """
        This section is executed when the interpreter encounters an error that is a BaseException but not an Exception.

        You can override this method and do what you need to do.
        It is recommended to keep throwing up at this point. These exceptions probably shouldn't stop there.

        :param exception: The exception
        :param args: The arguments
        """
        logger.exception(f"Error: {exception}")
        raise

    async def on_cancel(self, args: ParamsPackage[Params]) -> int | None | NoReturn:
        """
        This section is executed when the Handler is cancelled.

        You can override this method and do what you need to do.

        :param args: The args object
        """
        logger.warning(f"{self.package_name} cancelled")
        await args.output.put(f"Tool {self.package_name} was cancelled.")
        return None

    async def on_timeout(self, args: ParamsPackage[Params]) -> int | None | NoReturn:
        """
        This section is executed when the Handler times out.

        You can override this method and do what you need to do.

        :param args: The args object
        """
        logger.warning(f"{self.package_name} timed out")
        await args.output.put(f"Tool {self.package_name} timed out.")
        return None

    async def handler_exit(self, args: ParamsPackage[Params]) -> int | None | NoReturn:
        """
        This section is executed whenever the Handler fails or exits.

        You can override this method and do what you need to do.

        :param args: The args object
        :return: None
        """
        logger.info(f"{self.package_name} exited")
        return None

    # ------------------------------------------------------------------ #
    # Registration hooks
    # ------------------------------------------------------------------ #

    def on_registed(self):
        """
        You may want to do something when you complete the registration process,
        overriding this method allows you to perform the task at the end of the registration.

        :return: None
        """
        pass

    @classmethod
    def on_reg_failed(cls, exc_val: BaseException):
        """
        If an error occurs during the registration of the current Handler,
        by default, the behavior of the modified method is to throw the original exception.

        An override that returns instead of raising makes the framework skip the
        tool entirely.

        :param exc_val: Exception value
        :return: None
        """
        raise

    @classmethod
    def on_destroy(cls):
        """
        This method is executed when the current Handler is destroyed.
        Both instance and class methods are allowed.
        """
        pass

    @classmethod
    async def on_adestroy(cls):
        """
        The asynchronous method executes when the current Handler is destroyed.
        Both instance and class methods are allowed.
        """
        pass

    @classmethod
    def on_duplicate_type(cls):
        """
        This section is executed when the type is triggered by a duplicate type.

        You can override this method and do what you need to do.

        :param other: The other class
        """
        raise ValueError(f"Tool {cls.package_path()}'s type {cls.__name__} is already registered")

    @classmethod
    def on_duplicate_class_name(cls, other: "type[ToolPackage]"):
        """
        This section is executed when the class name is triggered by a duplicate class name.

        You can override this method and do what you need to do.

        :param other: The other class
        """
        raise ValueError(f"Handler class name {cls.package_path()} and {other.package_path()} is already registered")

    @classmethod
    def on_duplicate_package_name(cls, other: "type[ToolPackage]"):
        """
        This section is executed when the component is triggered by a duplicate component.

        You can override this method and do what you need to do.

        :param other: The other class
        """
        raise ValueError(f"Tool name {cls.package_path()} and {other.package_path()} is already registered")

    @classmethod
    def on_duplicate_package_type(cls, other: "type[ToolPackage]"):
        """
        This section is executed when the component is triggered by a duplicate component.

        You can override this method and do what you need to do.

        :param other: The other class
        """
        raise ValueError(f"Tool type {cls.package_path()} and {other.package_path()} is already registered")
