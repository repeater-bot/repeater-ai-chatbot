from ....global_config_manager import HTTPMethods
from typing import Any, Literal
from pydantic import BaseModel, Field
from .retry import Retry

class Request(BaseModel):
    type: Literal["request"] = "request"
    id: str = Field(..., description="The ID of the request, used to locate which Request returned the Response.")
    method: HTTPMethods = Field(HTTPMethods.GET, description="The HTTP method to use for the request.")
    url: str = Field("", description="The target URL of the request.")
    fail_to_retry: Retry | None = Field(None, description="Whether to retry the request if it fails.")
    query_params: dict[str, str] | None = Field(None, description="Query parameters to append to the request URL.")
    headers: dict[str, str] | None = Field(None, description="HTTP headers to send with the request.")
    cookies: dict[str, str] | None = Field(None, description="Cookies to attach to the request.")
    form_data: dict[str, str] | None = Field(None, description="Form-data to send with the request.")
    json_data: Any | None = Field(None, description="JSON data to send in the request body.")
    auth: tuple[str, str] | None = Field(None, description="Basic authentication credentials as a (username, password) tuple.")
    follow_redirects: bool = Field(True, description="Whether to automatically follow HTTP redirects.")
    timeout_seconds: int | float = Field(10, description="Request timeout in seconds.")
    verify_crawler_permissions: bool = Field(True, description="Whether to verify crawler permissions. If the `robot.txt` is in the cache, it won't be accessed again for some time.")
    exclude_crawler_user_agent: bool = Field(False, description="Whether to not actively add the `User-Agent` in the request header (turn off this option if you need to set 'User-Agent') .")