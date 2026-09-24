# Dispatch Ask Questions

向用户发起问题，并获取用户的回答

**注意：** 该工具要求 Dispatch 服务器中必须包含 `/echo` 与 `/npecho`，且在填参为空时等待用户输入。

接受三个参数
``` json
{
  "bot_id": "1234567890", // "The Bot id."
  "ask_prompt": "", // The question to ask the user.
  "timeout": 2400, // Timeout for the request.
}
```

返回结果
``` json
{
  "messages": [], // User's answer.
  "error": null, // An error occurred during parsing.
  "retcode": 0 // The response code returned by the target Handler.
}
```
由于该工具会直接返回响应结果文本，所以此处响应格式仅供参考