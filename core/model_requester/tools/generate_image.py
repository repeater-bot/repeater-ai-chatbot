from typing import Any
from ...context import ToolCallPackage, CallMode
from ...data_manager import PromptManager
from .._caller import ModelRequester
from ...clients.model_info import ModelInfo, SafeModelInfo
from pydantic import BaseModel, Field
from enum import StrEnum
from ...core.image import (
    generate_image,
    Request
)
from ...call_api.image import (
    ImagesResponse,
    UrlFile,
    Image
)

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    CONTENT_ONLY = "content_only"
    REASONING_ONLY = "reasoning_only"
    NEW_CONTENT_ONLY = "new_content_only"
    NEW_REASONING_ONLY = "new_reasoning_only"

@ModelRequester.reg_global_package
class GenerateImage(ToolCallPackage):
    name = "generate_image"
    description = "Send a request to generate an image."
    call_mode = CallMode.ASYNC
    
    class Params(BaseModel):
        model_id: str | None = Field(
            default=None, 
            description="Unique identifier used to locate and load the target model, if not specified, the model will be selected based on the user's preferences."
        )
        brief_summary: str = Field(
            default="", 
            description="The alternate text used after the image is generated."
        )
        prompt: str = Field(
            default="", 
            description="The prompt to generate an image."
        )
        images: list[UrlFile] | None = Field(
            default=None,
            description="The images to use as a reference for the generation."
        )
    
    class Result(BaseModel):
        images: list[str | None] = Field(
            default_factory=list,
            description="The generated images."
        )
        markdown_images: list[str] = Field(
            default_factory=list,
            description="The generated images as markdown."
        )

    async def call(self, args: Params):

        request = Request(
            model_id = args.model_id,
            images = args.images, # type: ignore
            prompt = args.prompt,
        )

        response = await generate_image(
            user_id = self.user_id,
            request = request,
            fastapi_request = self.fastapi_request,
        )

        if not isinstance(response, ImagesResponse):
            raise ValueError("Invalid response")

        if not response.data:
            raise ValueError("No images returned")

        return self.Result(
            images = [img.url for img in response.data],
            markdown_images = [f"![{args.brief_summary}]({img.url})" for img in response.data if img.url],
        )