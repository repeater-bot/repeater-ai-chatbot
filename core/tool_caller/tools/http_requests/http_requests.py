from __future__ import annotations
import json
import httpx
import asyncio
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from ....global_config_manager import HTTPMethods, ConfigManager
from ...framework import ToolsCaller, ToolPackage, RuntimePackage
from ....auxiliary.http import get_ssl_context, RepeaterTransport, PublicIPOnlyTransport
from loguru import logger
from typing import ClassVar
from pydantic import BaseModel, Field
from cachetools import TTLCache
from .request import Request
from .response import Response
from .sleep import Sleep
from .backoff import exponential_backoff_with_jitter

@ToolsCaller.register
class HTTPRequests(ToolPackage):

    class Params(BaseModel):
        base_url: str = Field("", description="The base URL shared by all requests.")
        base_headers: dict[str, str] | None = Field(None, description="The underlying request header shared by all requests.")
        base_cookies: dict[str, str] | None = Field(None, description="The base Cookie shared by all requests.")
        base_auth: tuple[str, str] | None = Field(None, description="The base Auth shared by all requests.")
        base_proxy: str | None = Field(None, description="The base proxy shared by all requests.")
        base_timeout: int | float = Field(5, description="Requests timeout in seconds.")
        requests: list[list[Request | Sleep] | Request | Sleep] = Field(..., description="Sending requests in batches using connection pooling (The outer list executes sequentially, and the inner list executes in parallel.).")
    
    class Result(BaseModel):
        responses: list[list[Response | None]] = Field(..., description="The responses of the requests.")
    
    name = "http_requests"
    description = "send a any method HTTP request to a URL and return the response."
    robots_cache: ClassVar[TTLCache[str, str, float] | None] = None
    
    def validation_method(self, method: HTTPMethods, runtime: RuntimePackage) -> bool:
        allowed_http_methods = runtime.global_configs.tool_calls.tools_configs.http_requests.allowed_http_methods
        if allowed_http_methods is None:
            return False
        elif isinstance(allowed_http_methods, list):
            return method in allowed_http_methods
        elif allowed_http_methods == "ALL":
            return True
        else:
            return False
    
    def __init__(self):
        # Tool instances are built at registration time, so the cache is sized
        # from the process wide configs instead of from a `RuntimePackage`.
        configs = ConfigManager.get_configs().tool_calls.tools_configs.http_requests
        self.init_cache(
            configs.robots_cache_size,
            configs.robots_cache_timeout,
        )
    
    @classmethod
    def init_cache(cls, size: int, timeout: float):
        if cls.robots_cache is None:
            cls.robots_cache = TTLCache(
                maxsize = size,
                ttl = timeout
            )
    
    @staticmethod
    def get_root_url(url: str) -> str:
        parsed = urlparse(url)
        # 组合：scheme://netloc
        root = f"{parsed.scheme}://{parsed.netloc}"
        return root
    
    async def crawler_header(self, runtime: RuntimePackage) -> dict[str, str]:
        return {
            "User-Agent": runtime.global_configs.system_identification.crawler_name,
        }
    
    # NOTE: `base_url` is the host here while `raw_url` is an httpx.URL, so the
    # `base_url != raw_url` comparison below is always true and the crawler check
    # therefore rewrites `client.base_url` on every call. It has been kept as the
    # old implementation had it, because repairing it turns "robots.txt is
    # effectively never enforced" into "robots.txt is enforced".
    async def verify_crawler_permissions(self, client: httpx.AsyncClient, url: str, runtime: RuntimePackage) -> bool:
        if client.base_url.host:
            base_url = client.base_url.host
        elif url:
            base_url = self.get_root_url(url)
        else:
            raise ValueError("base_url is None")
        
        raw_url = client.base_url
        if base_url != raw_url:
            client.base_url = base_url
            rewrite_url: bool = True
        else:
            rewrite_url: bool = False

        try:
            if self.robots_cache is None:
                raise RuntimeError("robots_cache is None")
            
            if base_url in self.robots_cache:
                text = self.robots_cache[base_url]
            else:
                response = await client.get(
                    "/robots.txt"
                )
                if response.status_code == 200:
                    text = response.text
                    self.robots_cache[base_url] = text
                else:
                    return True

            robot_file_parser = RobotFileParser()
            robot_file_parser.parse(text.splitlines())
            return robot_file_parser.can_fetch(
                runtime.global_configs.system_identification.crawler_name, url
            )
        except Exception:
            return True
        finally:
            if rewrite_url: 
                client.base_url = raw_url
    
    @staticmethod
    async def _send_request(
        client: httpx.AsyncClient,
        request: Request,
        headers: dict | None = None,
    ) -> httpx.Response:
        response = await client.request(
            request.method,
            request.url,
            params = request.query_params,
            headers = headers,
            cookies = request.cookies,
            data = request.form_data,
            json = request.json_data,
            auth = request.auth,
            follow_redirects = request.follow_redirects,
            timeout = request.timeout_seconds,
        )
        return response
            
    async def send_request(self, client: httpx.AsyncClient, request: Request, runtime: RuntimePackage) -> Response:
        if not self.validation_method(request.method, runtime):
            return Response(
                request_id = request.id,
                reason = f"HTTP method {request.method} is not allowed."
            )
        
        headers = request.headers
        if headers is None:
            headers = {}
        if not request.exclude_crawler_user_agent:
            headers.update(await self.crawler_header(runtime))
        
        if request.verify_crawler_permissions:
            if not await self.verify_crawler_permissions(client, request.url, runtime):
                return Response(
                    request_id = request.id,
                    reason = "Crawler permissions denied."
                )
        
        try:
            if request.fail_to_retry is None:
                response = await self._send_request(
                    client,
                    request,
                    headers,
                )
            else:
                for times in range(request.fail_to_retry.retries):
                    try:
                        response = await self._send_request(
                            client,
                            request,
                            headers,
                        )
                        if response.status_code in request.fail_to_retry.status_codes:
                            raise httpx.HTTPStatusError(
                                f"HTTP status error: {response.status_code}",
                                request = response.request,
                                response = response,
                            )
                        break
                    except httpx.HTTPStatusError as e:
                        logger.error(
                            "HTTP status error: {message}",
                            message = str(e)
                        )
                    except httpx.HTTPError as e:
                        logger.error(
                            "HTTP error: {message}",
                            message = str(e)
                        )
                    
                    response = None
                    
                    await asyncio.sleep(
                        exponential_backoff_with_jitter(
                            times,
                            base_delay = request.fail_to_retry.backoff,
                            with_jitter = request.fail_to_retry.jitter
                        )
                    )
                
                if response is None:
                    return Response(
                        request_id = request.id,
                        reason = "The number of retries has run out."
                    )
        except httpx.TimeoutException:
            return Response(
                request_id = request.id,
                reason = "Timeout"
            )
        except httpx.HTTPError as e:
            return Response(
                request_id = request.id,
                reason = f"Error: {e}"
            )
        
        if response is not None:
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text
    
            return Response(
                request_id = request.id,
                status_code = response.status_code,
                reason = "Success",
                headers = dict(response.headers),
                cookies = dict(response.cookies),
                data = data,
            )
        else:
            return Response(
                request_id = request.id,
                reason = "No response"
            )

    def init_client(self, args: Params, allow_private_ip: bool = False):
        if allow_private_ip:
            transport = RepeaterTransport(
                verify = get_ssl_context(),
                proxy = args.base_proxy
            )
        else:
            transport = PublicIPOnlyTransport(
                verify = get_ssl_context(),
                proxy = args.base_proxy
            )

        client = httpx.AsyncClient(
            base_url = args.base_url,
            headers = args.base_headers,
            cookies = args.base_cookies,
            auth = args.base_auth,
            timeout = args.base_timeout,
            transport = transport
        )
        return client

    async def call(self, args: Params, runtime: RuntimePackage):
        configs = ConfigManager.get_configs().tool_calls.tools_configs.http_requests
        client = await asyncio.to_thread(
            self.init_client,
            args,
            allow_private_ip = configs.allow_private_network_requests
        )

        responses: list[list[Response | None]] = []
        
        for requests in args.requests:
            # NOTE: the old implementation kept one task set for every batch, so
            # each later batch re-gathered (and re-reported) the responses of the
            # earlier ones. The set is per batch here, which is what the field
            # description promises.
            tasks: set[asyncio.Task[Response | None]] = set()
            if isinstance(requests, list):
                for request in requests:
                    if isinstance(request, Request):
                        tasks.add(
                            asyncio.create_task(
                                self.send_request(
                                    client,
                                    request,
                                    runtime,
                                )
                            )
                        )
                    elif isinstance(request, Sleep):
                        tasks.add(
                            asyncio.create_task(
                                request.sleep()
                            )
                        )
            elif isinstance(requests, Request):
                tasks.add(
                    asyncio.create_task(
                        self.send_request(
                            client,
                            requests,
                            runtime,
                        )
                    )
                )
            elif isinstance(requests, Sleep):
                await requests.sleep()
            
            results = await asyncio.gather(*tasks)
            responses.append(results)
        
        return self.Result(
            responses = responses,
        ).model_dump(exclude_none = True)
