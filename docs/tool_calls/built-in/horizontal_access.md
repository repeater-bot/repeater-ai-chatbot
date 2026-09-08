# Horizontal Access

横向发起对其他实例的聊天请求

注册名：`horizontal_access`

接受四个参数
``` json
{
  "instance_id": "", // The instance ID to access.
  "message": "", // The message to send to the instance.
  "thinking": false, // Whether to show thinking indicator.
  "timeout": 600 // The timeout for the request.
}
```

返回响应获取的聊天记录
``` python
{
    "context_list": [
        {
            "reasoning_content": null,
            "content": "",
            "role": "assistant",
            "role_name": null,
            "prefix": null,
            "created": "2023-12-08T16:00:00.000000",
            "tool_calls": null,
            "tool_call_id": null
        }
    ]
}
```