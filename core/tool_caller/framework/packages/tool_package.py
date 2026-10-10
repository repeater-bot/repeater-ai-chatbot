import uuid
import httpx
import textwrap

from pydantic import BaseModel
from abc import (
    ABC,
    abstractmethod
)
from typing import (
    Any,
    Generic,
    Iterable,
    Type,
    TypeVar,
    NoReturn,
)
from ..typings import (
    New
)
from ....auxiliary.type_checker import is_iterable
from .params_package import ParamsPackage
from loguru import logger

class ToolPackage(ABC):
    """
    Tool Package Base Class
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
    """The name of the tool package"""

    package_type: str = "Default"
    """Package Type"""

    name: str | None = None
    """Name of the tool package"""

    enabled: bool = True
    """Whether the handler."""

    description: str | Iterable[str] | None = None
    """This handler's description"""

    docs_delimiter: str = "\n"
    """Documentation delimiter"""

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
    
    async def enter_handler(self, args: ParamsPackage) -> int:
        """
        This method is called before the handler method.

        :param args: Parameters for the tool.
        :return: The result of the handler method.
        """
        result = await self.handler(args)
        return result

    @abstractmethod
    async def handler(self, args: ParamsPackage) -> int:
        """
        Override this method to begin writing your business logic.

        :param args: Parameters for the tool.
        :return: The result of the tool.
        """
        pass

    async def on_error(self, exception: Exception, args: ParamsPackage) -> int | None | NoReturn:
        """
        The error Handler for the Handler

        It catches all exceptions by default

        Includes all the necessary parts for the framework to work

        So you need to determine them and re-throw them to make sure the framework is working properly

        :param exception: The exception
        :param args: Parameters for the tool.
        :return: The result of the tool.
        :raises: The exception
        """
        await args.output.put(f"Error: {exception}")
        return -1
    
    async def on_interpreter_error(self, exception: BaseException, args: ParamsPackage) -> int | None | NoReturn:
        """
        This section is executed when the interpreter encounters an error that is a BaseException but not an Exception.

        You can override this method and do what you need to do.
        It is recommended to keep throwing up at this point. These exceptions probably shouldn't stop there.

        :param exception: The exception
        :param args: The arguments
        """
        logger.exception(f"Error: {exception}")
        raise
    
    async def on_cancel(self, args: ParamsPackage) -> int | None | NoReturn:
        """
        This section is executed when the Handler is cancelled.

        You can override this method and do what you need to do.

        :param args: The args object
        """
        logger.warning(f"{self.package_name} cancelled")
        return None

    async def on_timeout(self, args: ParamsPackage) -> int | None | NoReturn:
        """
        This section is executed when the Handler times out.

        You can override this method and do what you need to do.

        :param args: The args object
        """
        logger.warning(f"{self.package_name} timed out")
        return None
    
    async def handler_exit(self, args: ParamsPackage) -> int | None | NoReturn:
        """
        This section is executed whenever the Handler fails or exits.

        You can override this method and do what you need to do.

        :param args: The args object
        :return: None
        """
        logger.info(f"{self.package_name} exited")
        return None
    
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