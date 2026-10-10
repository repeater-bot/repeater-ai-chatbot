from ..framework import ToolsCaller, ToolPackage, RuntimePackage
from ...call_api.image import (
    ImagesResponse,
    UrlFile,
)
from pydantic import BaseModel, Field
from ...core.image import (
    generate_image,
    Request
)

@ToolsCaller.register
class GenerateImage(ToolPackage):
    name = "generate_image"
    description = "Send a request to generate an image."
    
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

    async def call(self, args: Params, runtime: RuntimePackage):

        request = Request(
            model_id = args.model_id,
            images = args.images, # type: ignore
            prompt = args.prompt,
        )

        response = await generate_image(
            user_id = runtime.user_id,
            request = request,
            fastapi_request = runtime.fastapi_request,
        )

        if not isinstance(response, ImagesResponse):
            raise ValueError("Invalid response")

        if not response.data:
            raise ValueError("No images returned")

        return self.Result(
            images = [img.url for img in response.data],
            markdown_images = [f"![{args.brief_summary}]({img.url})" for img in response.data if img.url],
        )
