from ...context import ToolCallPackage, ImageBlock, ImageUrlBlock, ContentResult
from .._caller import ModelRequester
from pydantic import BaseModel, Field

@ModelRequester.reg_global_package
class URLToImage(ToolCallPackage):
    class Params(BaseModel):
        urls: list[str] = Field(..., description="The URLs of the images to read")
    
    name = "url_to_image"
    array_result = True
    description = "Read the image content in the URL (requires the model to support passing in images in tool calls and only public urls can be passed) ."

    def call(self, args: Params):
        return ContentResult(
            content = [
                ImageBlock(
                    image_url = ImageUrlBlock(
                        url = url
                    )
                )
                for url in args.urls
            ]
        )