# Dispatch Trigger

按 Repeater 客户端通信协议向客户端发起触发请求
需在 `tool_calls.tools_configs.dispatch_trigger` 中配置客户端地址

注册名：`dispatch_trigger`

接受六个参数
``` json
{
  "bot_id": "", // The Bot id.
  "handler": "", // The target Handler that needs to be executed uses a Trigger match if it starts with a slash and a component ID match if it starts without a slash.
  "message": "", // The cq.code message that needs to be sent.
  "args": null, // Optionally, the message data will be overwritten when args is present.
  "message_id": 0, // Message ID, which identifies the ID of the current message.
  "timeout": 2400, // Timeout for the request.
}
```

返回结果
``` json
{
  "messages": [], // Copy back the results of the execution.
  "error": null, // An error occurred during parsing.
  "retcode": 0 // The response code returned by the target Handler.
}
```
由于该工具会直接返回响应结果文本，所以此处响应格式仅供参考