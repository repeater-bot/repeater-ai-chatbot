import sys
import asyncio
from io import StringIO
from typing import Any, TextIO
from ...context import ToolCallPacakage, CallMode
from .._caller import ModelRequester
from asteval import Interpreter
from pydantic import BaseModel, Field

@ModelRequester.reg_global_package
class Asteval(ToolCallPacakage):
    class Params(BaseModel):
        expression: str | list[str] = Field(..., description="The Python expression to evaluate. (Ban high-risk functions.)")
        symbols: dict[str, Any] | None = Field(None, description="The symbols to use in the evaluation. ")
        timeout: int | float | None = Field(5, description="The timeout for the evaluation.")
    
    class Result(BaseModel):
        result: Any = Field(..., description="The result of the evaluation.")
        stdout: str = Field("", description="The standard output of the evaluation.")
        stderr: str = Field("", description="The standard error of the evaluation.")
    
    name = "asteval"
    docdescriptionument = "Execute Python code safely and return results."
    call_mode = CallMode.ASYNC

    @staticmethod
    def safe_eval(
        aeval: Interpreter,
        expression: str | list[str]
    ) -> Any:
        try:
            if isinstance(expression, str):
                return aeval.eval(
                    expression,
                    raise_errors = True,
                )
            else:
                return [
                    aeval.eval(
                        expr,
                        raise_errors = True,
                    ) for expr in expression
                ]
        except Exception as e:
            return e
    
    def _open(self, *args, **kwargs) -> None:
        raise NotImplementedError
    
    def _input(self, *args, **kwargs) -> None:
        raise NotImplementedError
    
    class InterpreterStdout(StringIO):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def readable(self) -> bool:
            return False
        
        def writable(self) -> bool:
            return True

    class InterpreterStderr(StringIO):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def readable(self) -> bool:
            return False

        def writable(self) -> bool:
            return True

    async def call(self, args: Params) -> Any:
        stdout = self.InterpreterStdout()
        stderr = self.InterpreterStderr()
        aeval = Interpreter(
            writer = stdout,
            err_writer  = stderr,
            use_numpy = False,
            user_symbols = args.symbols,
            builtins_readonly = True,
        )
        
        aeval.symtable.update(
            {
                "open": self._open,
                "input": self._input,
            }
        )
        
        task = asyncio.create_task(
            asyncio.to_thread(
                self.safe_eval,
                aeval,
                args.expression
            )
        )

        try:
            result = await asyncio.wait_for(task, args.timeout)
        except asyncio.TimeoutError:
            task.cancel()
            return "Expression execution timed out."
        return self.Result(
            result = repr(result),
            stdout = stdout.getvalue(),
            stderr = stderr.getvalue(),
        )