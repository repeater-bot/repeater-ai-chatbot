from __future__ import annotations
import json
import httpx
from environs import Env
from pydantic import BaseModel, Field
from ....context import ToolCallPackage, CallMode
from ....auxiliary.http import get_ssl_context
from ..._caller import ModelRequester
from .scope import Scope

@ModelRequester.reg_global_package
class Metaso(ToolCallPackage):

    class Params(BaseModel):
        q: str = Field(..., description="The query to search for")
        scope: Scope = Field(Scope.WEBPAGE, description="The scope to search in")
        includeSummary: bool = Field(False, description="Whether to include a summary of the results")
        size: str = Field("10", description="The number of results to return")
        includeRawContent: bool = Field(False, description="Whether to include the raw content of the results")
        conciseSnippet: bool = Field(False, description="Whether to include a concise snippet of the results")
    
    class Result(BaseModel):
        static_code: int = Field(..., description="The status code of the response")
        data: dict = Field(..., description="The data of the response")
    
    name = "metaso"
    call_mode = CallMode.ASYNC
    json_result = True
    _env = Env()
    client: httpx.AsyncClient | None = None
    description = "Metaso Internet AI Search"

    async def call(self, args: Params):
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url = "https://metaso.cn/api/v1",
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._env.str('METASO_API_KEY')}"
                },
                verify = get_ssl_context()
            )
        
        response = await self.client.post(
            "/search",
            json = args.model_dump()
        )
        return self.Result(
            static_code = response.status_code,
            data = response.json()
        )