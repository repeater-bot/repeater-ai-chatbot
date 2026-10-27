from __future__ import annotations
import re
import httpx
from typing import Any
from environs import Env
from pydantic import BaseModel, Field
from ....runtime_container import RuntimeContainer
from ....auxiliary.http import get_ssl_context
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from .client import deepseek_api_client

@ToolsCaller.register
class DeepseekFetch(ToolPackage):

    class Params(BaseModel):
        url: str = Field(
            ...,
            description="The URL to fetch. Must be at most 8192 characters and an HTTP or HTTPS URL with a host. The URL must not contain a username or password."
        )
     
    
    class Result(BaseModel):
        static_code: int = Field(..., description="The status code of the response")
        data: Any = Field(..., description="The data returned by the server")
    
    name = "deepseek_api_fetch"
    description = "Fetch a web page and return its title and content as Markdown. See the Search & Fetch guide for error handling and billing. (using DeepSeek API)"

    def headers(self, env: Env):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env.str('DEEPSEEK_API_KEY')}"
        }
        return headers

    async def call(self, args: Params, runtime: RuntimePackage):
        global_runtime = RuntimeContainer.get_runtime()
        env = global_runtime.env
        
        response = await deepseek_api_client.post(
            "https://api.deepseek.com/v1/tools/search",
            headers = self.headers(env),
            json = args.model_dump()
        )
        return self.Result(
            static_code = response.status_code,
            data = response.json()
        )
