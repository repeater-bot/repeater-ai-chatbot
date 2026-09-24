import asyncio
import starlark
from typing import Any
from ...context import ToolCallPackage, CallMode
from .._caller import ModelRequester
from pydantic import BaseModel, Field

@ModelRequester.reg_global_package
class Starlark(ToolCallPackage):
    class Params(BaseModel):
        source: str = Field(..., description="The starlark code source.")
        root_stack_frame_name: str = Field(default="<repeater_starlark_interpreter>", description="The name of the root stack frame.")
        predeclared: dict[str, Any] | None = Field(default=None, description="The variables to declare before evaluating the expression.")
        universal: dict[str, Any] | None = Field(default=None, description="The variables to declare before evaluating the expression.")
        max_steps: int | None = Field(default=None, description="The maximum number of steps to execute. (Default: None)")
        max_allocs: int | None = Field(default=None, description="The maximum number of allocations to execute. (Default: None)")
        timeout: int | float | None = Field(5, description="The timeout for the evaluation.")
    
    class Result(BaseModel):
        result: str | None = Field(default=None, description="The result of the evaluation.")
        error: str | None = Field(default=None, description="The error message if the evaluation failed.")
        traceback: str | None = Field(default=None, description="The traceback of the evaluation.")
    
    name = "starlark"
    description = "Execute Starlark code and return results."
    call_mode = CallMode.ASYNC
    json_result = True

    @staticmethod
    def program_eval(
        program: starlark.Program,
        predeclared: dict[str, Any] | None = None,
        universal: dict[str, Any] | None = None,
        max_steps: int | None = None,
        max_allocs: int | None = None,
    ) -> Any:
        return program.eval(
            predeclared = predeclared,
            universal = universal,
            max_steps = max_steps,
            max_allocs = max_allocs,
        )

    @classmethod
    def run_code(
        cls,
        source: str,
        filename = "<repeater_starlark_interpreter>",
        mode: str = "expression",
        predeclared: dict[str, Any] | None = None,
        universal: dict[str, Any] | None = None,
        max_steps: int | None = None,
        max_allocs: int | None = None,
    ) -> Any:
        return cls.program_eval(
            program=starlark.compile(
                source = source,
                filename = filename,
                mode = mode
            ),
            predeclared = predeclared,
            universal = universal,
            max_steps = max_steps,
            max_allocs = max_allocs
        )

    async def call(self, args: Params) -> Any:
        configs = self.global_configs.tool_calls.tools_configs.starlark
        max_steps = max(args.max_steps or configs.default_max_steps, configs.force_max_steps)
        max_allocs = max(args.max_allocs or configs.default_max_allocs, configs.force_max_allocs)
        
        task = asyncio.create_task(
            asyncio.to_thread(
                self.run_code,
                source = args.source,
                filename = args.root_stack_frame_name,
                predeclared = args.predeclared,
                universal = args.universal,
                max_steps = max_steps,
                max_allocs = max_allocs
            )
        )

        try:
            result = await asyncio.wait_for(task, args.timeout)
        except ValueError as e:
            return self.Result(
                error = str(e)
            ).model_dump(exclude_none = True)
        except starlark.EvalError as e:
            text_buffer: list[str] = []
            for index, frame in enumerate(e.frames):
                text_buffer.append(f"[{index}]: {frame.name}: {frame.position}")
            text_buffer.append("")
            text_buffer.append(f"{e.message}")
            return self.Result(
                traceback = "\n".join(text_buffer)
            ).model_dump(exclude_none = True)
        except asyncio.TimeoutError:
            task.cancel()
            return self.Result(
                error = "Expression execution timed out."
            ).model_dump(exclude_none = True)
        return self.Result(
            result = repr(result)
        ).model_dump(exclude_none = True)