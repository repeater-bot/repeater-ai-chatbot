from pydantic import BaseModel, Field
from ...context import ToolCallPackage, CallMode
from ...data_manager import PromptManager
from .._caller import ModelRequester
from ...runtime_container import RuntimeContainer
from ...clients.model_info import SafeModelInfo

@ModelRequester.reg_global_package
class GetModels(ToolCallPackage):
    prompt_manager: PromptManager = PromptManager()
    name = "get_models"
    description = "Gets a list of all available models."
    call_mode = CallMode.ASYNC

    class Params(BaseModel):
        model_id: str | list[str] | None = Field(None, description = "Model query expression.")
        detailed_info: bool = Field(False, description = "More detailed model information.")
    
    class Result(BaseModel):
        models: list[SafeModelInfo] = Field(default_factory=list)

    async def call(self, args: Params):
        runtime = RuntimeContainer.get_runtime()
        if args.model_id is None:
            model_id = self.user_configs.model_id
            if model_id is None:
                model_id = self.global_configs.model_api.default_model_id
        else:
            model_id = args.model_id
        models = await runtime.model_info_client.get_model_list(model_id)
        
        return self.Result(
            models = [model.to_safe(detailed_info = args.detailed_info) for model in models]
        )