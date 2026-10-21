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
class DeepseekSearch(ToolPackage):

    class Params(BaseModel):
        query: str = Field(
            ...,
            description="The search query. Supports operators such as `site:`, `-site:`, and quoted phrases. Must contain 1 to 128 Unicode characters and cannot be all whitespace."
        )
        count: int = Field(
            default = 10,
            description="The number of results to return, between 1 and 50. Defaults to 10.",
            ge = 1,
            le = 50
        )
        ori_question: str | None = Field(
            default = None,
            description="The user's original question that triggered the search, between 1 and 128 characters. Providing it can improve query understanding. `null` is treated as not provided."
        )
        localization: str | None = Field(
            default = None,
            description="An optional IP address used to localize search results. Defaults to an empty string."
        )
        need_content: bool = Field(
            default = False,
            description="Whether to return page content in `content`. Defaults to `false`; when `false`, `content` is always an empty string."
        )
     
    
    class Result(BaseModel):
        static_code: int = Field(..., description="The status code of the response")
        data: Any = Field(..., description="The data returned by the server")
    
    name = "deepseek_api.search"
    description = "Search the web for a query and return a ranked list of structured results. See the Search & Fetch guide for supported query operators, error handling, and billing. (using DeepSeek API)"

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
