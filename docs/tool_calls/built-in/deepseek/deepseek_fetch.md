# Deepseek Fetch

Deepseek Fetch API 适配
使用它你需要配置环境变量 `DEEPSEEK_API_KEY`

注册名：`deepseek_api_fetch`

接受一个参数：
``` json
{
  "url": "", // The URL to fetch. Must be at most 8192 characters and an HTTP or HTTPS URL with a host. The URL must not contain a username or password.
}
```

返回结果：
``` json
{
  "static_code": 200, // The static code of the response
  "data": {...} // The data of the response
}
```