from pydantic import BaseModel, Field
from ...runtime_container import RuntimeContainer
from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from ...clients.model_info import SafeModelInfo

@ToolsCaller.register
class GetModels(ToolPackage):
    name = "get_models"
    description = "Gets a list of all available models."

    class Params(BaseModel):
        model_id: str | list[str] | None = Field(None, description = "Model query expression.")
        detailed_info: bool = Field(False, description = "More detailed model information.")
    
    class Result(BaseModel):
        models: list[SafeModelInfo] = Field(default_factory=list)

    async def call(self, args: Params, runtime: RuntimePackage):
        if args.model_id is None:
            model_id = runtime.user_configs.model_id
            if model_id is None:
                model_id = runtime.global_configs.model_api.default_model_id
        else:
            model_id = args.model_id
        models = await RuntimeContainer.get_runtime().model_info_client.get_model_list(model_id)
        
        return self.Result(
            models = [model.to_safe(detailed_info = args.detailed_info) for model in models]
        )
