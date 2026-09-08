# HTTP Requests Tool

该工具用于发送 HTTP 请求
如需访问内网需要配置 `tool_calls.allow_private_network_requests` 为 `true`
如需支持使用所有 HTTP 方法需要配置 `tool_calls.tools_configs.http_requests.allowed_http_methods` 为 `ALL` 或手动写出所有方法

注册名：`http_requests`

接受参数：
``` json
{
  "base_url": "", // The base URL shared by all requests.
  "base_headers": null, // The underlying request header shared by all requests.
  "base_cookies": null, // The base Cookie shared by all requests.
  "base_auth": null, // The base Auth shared by all requests.
  "base_proxy": null, // The base Proxy shared by all requests.
  "base_timeout": 5, // Requests timeout in seconds.
  "requests": [ // Sending requests in batches using connection pooling (The outer list executes sequentially, and the inner list executes in parallel.).
    [
      {
        "type": "request", // The type of request.
        "method": "GET", // The HTTP method to use for the request.
        "id": "parallel_request", // The ID of the request, used to locate which Request returned the Response.
        "url": "", // The target URL of the request.
        "fail_to_retry": null, // Whether to retry the request if it fails.
        "query_params": null, // Query parameters to include in the request URL.
        "headers": null, // HTTP headers to send with the request.
        "cookies": null, // Cookies to attach to the request.
        "form_data": null, // Form-data to send with the request.
        "json_data": null, // JSON data to send in the request body.
        "auth": null, // Basic authentication credentials as a (username, password) tuple.
        "follow_redirects": true, // Whether to automatically follow HTTP redirects.
        "timeout_seconds": 10, // Request timeout in seconds.
        "verify_crawler_permissions": true, // Whether to verify crawler permissions. If the `robot.txt` is in the cache, it won't be accessed again for some time.
        "exclude_crawler_user_agent": false // Whether to not actively add the `User-Agent` in the request header (turn off this option if you need to set 'User-Agent') .
      },
      {
        "type": "sleep", // The type of sleep.
        "sleep_seconds": 10 // Sleep in a batch affects the end time of the batch.
      }
    ],
    {
      "type": "sleep",
      "sleep_seconds": 10.0 // Sleep on the outside suspends requests on the back end.
    },
    {
      // If the batch had only one request, it could be written like this.
      "type": "request",
      "id": "serial_request",
      "method": "GET",
      "url": "https://example.com",
      "fail_to_retry": {
        "status_codes": [500, 502, 503, 504], // The HTTP status codes to retry on.
        "retiry": 3, // Retry 3 times
        "backoff": 1.0, // Backoff Index (1.0, 2.0, 4.0, ...)
        "jitter": 0.0 // No jitter
      }
    }
  ]
}
```

然后拿到响应对象列表

```json
{
  "responses":[
    {
      "request_id": "", // The ID of the request.
      "status_code": 200, // HTTP Status Code
      "reason": "success", // As long as the response is `success` and timeouts and the like will be something else
      "response_time": "", // The time it took to get the response
      "headers": {}, // Response headers
      "cookies": {}, // Response cookie
      "request": {},  // Request object
      "data": {} // The response content (if the JSON parsing fails, the response text is returned as `data` ; if the parsing succeeds, the field is any JSON object) 
    }
  ]
}
```