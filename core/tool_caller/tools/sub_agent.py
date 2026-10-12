from typing import Any
from ...call_api.completions_api import (
    Request,
    Runtime,
    StreamOptions
)
from ...user_data_managers.context import (
    Context,
    ContentRole,
    ContentUnit
)
from ...global_config_manager import ReasoningEffort
from ...model_requester import ModelRequester
from ...runtime_container import RuntimeContainer
from ...text_buffer import ContentBuffer, TextBuffer
from ...clients.model_info import ModelInfo, SafeModelInfo
from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from pydantic import BaseModel, Field
from enum import StrEnum
from loguru import logger

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    CONTENT_ONLY = "content_only"
    REASONING_ONLY = "reasoning_only"
    NEW_CONTENT_ONLY = "new_content_only"
    NEW_REASONING_ONLY = "new_reasoning_only"

@ToolsCaller.register
class SubAgent(ToolPackage):
    name = "sub_agent"
    description = "Assign a simple task to a sub-Agent, and when it finishes running, it doesn't quit, it waits for a new input. Please use the cancel task to close."
    
    class Params(BaseModel):
        model_id: str = Field(
            default="", 
            description="Unique identifier used to locate and load the target model."
        )
        user_name: str = Field(
            default="", 
            description="Name of the user making the request, used for logging and personalization."
        )
        temperature: float = Field(
            default=1.0, 
            ge=0.0, 
            le=2.0, 
            description="Controls randomness in output. Lower values (e.g., 0.2) make output more deterministic; higher values (e.g., 1.5) increase diversity. Must be between 0 and 2."
        )
        top_p: float = Field(
            default=1.0, 
            ge=0.0, 
            le=1.0, 
            description="Nucleus sampling threshold. The model considers only the smallest set of tokens whose cumulative probability >= top_p. Must be between 0 and 1."
        )
        presence_penalty: float = Field(
            default=0.0, 
            ge=-2.0, 
            le=2.0, 
            description="Penalizes tokens that have appeared at all in the text so far, encouraging the model to talk about new topics. Positive values discourage repetition. Range: -2.0 to 2.0."
        )
        frequency_penalty: float = Field(
            default=0.0, 
            ge=-2.0, 
            le=2.0, 
            description="Penalizes tokens proportionally to how often they have appeared, reducing verbatim repetition. Positive values discourage frequent tokens. Range: -2.0 to 2.0."
        )
        max_tokens: int = Field(
            default=4096, 
            gt=0, 
            description="The maximum number of tokens the model can generate in the response."
        )
        max_completion_tokens: int = Field(
            default=4096, 
            gt=0, 
            description="Alias for max_tokens. The maximum number of tokens allowed in the completion output."
        )
        thinking: bool | None = Field(
            default=None, 
            description="When enabled, the model allocates tokens for internal reasoning before producing the final answer. Useful for complex, multi-step problems."
        )
        stop: list[str] | None = Field(
            default=None, 
            description="List of strings where the model stops generating further tokens when encountered."
        )
        context: Context | None = Field(
            default=None, 
            description="Predefined conversation history or system context to guide the model's behavior."
        )
        allow_tools: list[str] | None = Field(
            default=None, 
            description="List of tool names that the model is allowed to use."
        )
        reasoning_effort: ReasoningEffort | None = Field(
            default=None, 
            description="Controls how many tokens the model spends on internal reasoning (e.g., 'low', 'medium', 'high')."
        )
        remove_reasoning_prompt: bool = Field(
            default=False, 
            description="If True, strips the internal reasoning prompt from the output, returning only the final answer."
        )
        output_role: ContentRole = Field(
            default=ContentRole.ASSISTANT, 
            description="Role assigned to the generated content in the conversation structure (e.g., 'assistant')."
        )
        timeout: int | float | None = Field(
            default=None, 
            gt=0, 
            description="Maximum time in seconds to wait for a response before the request is cancelled."
        )
        output_format: OutputFormat = Field(
            default=OutputFormat.TEXT, 
            description="Format of the output data returned by the API (e.g., 'text')."
        )
        extra_bodys: dict[str, Any] = Field(
            default_factory=dict, 
            description="Additional parameters to pass to the API call."
        )
    
    class Result(BaseModel):
        model: SafeModelInfo = Field(description="The model used for the API call.")
        context: Context = Field(description="The context used for the API call.")
    
    @staticmethod
    def response_parser(
        model: ModelInfo,
        context: Context,
        include_reasoning: bool = True,
        include_content: bool = True,
    ):
        for index, content in enumerate(context):
            yield f"<content index: \"{index}\" role: \"{content.role}\" model: \"{model.name}\">"
            if include_reasoning and content.reasoning_content:
                yield "<think>"
                yield content.reasoning_content
                yield "</think>"
            if include_content and content.content:
                yield content.content_to_string()
            yield "</content>"

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        
        model = await global_runtime.model_info_client.get_random_model(
            model_id = args.model_id
        )
        
        if runtime.user_configs.send_user_id is not None:
            send_user_id = runtime.user_configs.send_user_id
        else:
            send_user_id = runtime.global_configs.callapi.send_user_id
        
        if model.api_key is None:
            raise Exception("Model api key is not set")

        extra_bodys: dict[str, Any] = {}
        if runtime.global_configs.model.enable_user_extra_bodys:
            extra_bodys.update(args.extra_bodys)
        if runtime.global_configs.model.extra_bodys is not None:
            extra_bodys.update(runtime.global_configs.model.extra_bodys)
        if runtime.global_configs.model.enable_user_extra_bodys and runtime.user_configs.extra_bodys is not None:
            extra_bodys.update(runtime.user_configs.extra_bodys)
        if runtime.global_configs.model.extra_bodys_priority is not None:
            extra_bodys.update(runtime.global_configs.model.extra_bodys_priority)
            
        if runtime.global_configs.tool_calls.enabled:
            tool_calls_configs = runtime.global_configs.tool_calls
            server_registed_tools = tool_calls_configs.registed
            if runtime.user_configs.allowed_tool_calls:
                user_registed_tools = runtime.user_configs.allowed_tool_calls
            elif tool_calls_configs.allowed_by_default:
                user_registed_tools = tool_calls_configs.allowed_by_default
            else:
                user_registed_tools = set()

            available_tool_calls = server_registed_tools.intersection(user_registed_tools)
        else:
            available_tool_calls = set()

        if args.allow_tools:
            allowed_tool_calls = set(args.allow_tools).intersection(available_tool_calls)
        else:
            allowed_tool_calls = set()

        context: Context = args.context or Context()
        outputs: list[str] = []

        while True:
            request = Request(
                url = model.get_base_url(),
                limits = model.limits,
                key = model.api_key,
                timeout = args.timeout if args.timeout is not None else model.timeout,
                model = model.id,
                model_id = args.model_id,
                model_uid = model.uid,
                user_name = args.user_name,
                temperature = args.temperature,
                top_p = args.top_p,
                presence_penalty = args.presence_penalty,
                frequency_penalty = args.frequency_penalty,
                max_tokens = args.max_tokens,
                max_completion_tokens = args.max_completion_tokens,
                thinking = args.thinking,
                stop = args.stop,
                context = context,
                reasoning_effort = args.reasoning_effort,
                remove_reasoning_prompt = args.remove_reasoning_prompt,
                remove_created = True,
                send_user_id = send_user_id,
                stream = runtime.global_configs.model.stream,
                stream_options = StreamOptions(
                    include_obfuscation = runtime.global_configs.callapi.include_obfuscation,
                    include_usage = runtime.global_configs.callapi.include_usage
                ),
                extra_bodys = extra_bodys,
            )
            
            request_runtime = Runtime(
                client_pool = global_runtime.openai_pool,
                content_buffer = ContentBuffer()
            )
            
            requestser = ModelRequester(
                user_id = runtime.user_id,
                user_configs = runtime.user_configs,
                global_configs = runtime.global_configs,
                fastapi_request = runtime.fastapi_request,
                model_info_client = global_runtime.model_info_client,
                max_concurrency = runtime.global_configs.callapi.max_concurrency
            )

            responses = await requestser.submit(
                user_id = runtime.user_id,
                request = request,
                runtime = request_runtime,
                available_tool_calls = allowed_tool_calls,
                stream = False
            )

            new_context = responses.new_contexts()
            match args.output_format:
                case OutputFormat.TEXT:
                    buffer = TextBuffer(separator = "\n")
                    buffer.consume_iterable_no_conversion(
                        self.response_parser(
                            model,
                            new_context
                        )
                    )
                    output = str(buffer)
                case OutputFormat.JSON:
                    output = self.Result(
                        model = model.to_safe(),
                        context = new_context,
                    ).model_dump_json()
                case OutputFormat.CONTENT_ONLY:
                    buffer = TextBuffer(separator = "\n")
                    buffer.consume_iterable_no_conversion(
                        self.response_parser(
                            model,
                            new_context,
                            include_content = True,
                            include_reasoning = False,
                        )
                    )
                    output = str(buffer)
                case OutputFormat.REASONING_ONLY:
                    buffer = TextBuffer(separator = "\n")
                    buffer.consume_iterable_no_conversion(
                        self.response_parser(
                            model,
                            new_context,
                            include_content = False,
                            include_reasoning = True,
                        )
                    )
                    output = str(buffer)
                case OutputFormat.NEW_CONTENT_ONLY:
                    last_content = new_context.last_content
                    if last_content is None:
                        output = ""
                    else:
                        output = last_content.content_to_string()
                case OutputFormat.NEW_REASONING_ONLY:
                    last_content = new_context.last_content
                    if last_content is None:
                        output = ""
                    else:
                        output = str(last_content.reasoning_content)
            outputs.append(output)
            await runtime.output.put(output)
            if runtime.user_configs.remove_reasoning_prompt is not None:
                if runtime.user_configs.remove_reasoning_prompt:
                    new_context.remove_reasoning_content()
            else:
                if runtime.global_configs.context.remove_reasoning_prompt:
                    new_context.remove_reasoning_content()
            context.extend(new_context)
            while True:
                input_next = await runtime.input.wait()
                if not isinstance(input_next, str):
                    logger.warning(
                        "SubAgent input is not a string",
                        user_id = runtime.user_id
                    )
                    continue

                new_content = ContentUnit(
                    content = input_next,
                    role = ContentRole.USER,
                )
                context.append(new_content)
                break