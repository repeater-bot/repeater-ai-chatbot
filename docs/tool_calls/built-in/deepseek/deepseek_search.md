# Deepseek Search

Deepseek Search API 适配
使用它你需要配置环境变量 `DEEPSEEK_API_KEY`

注册名：`deepseek_api_search`

接受五个参数：
``` json
{
  "query": "", // The search query. Supports operators such as `site:`, `-site:`, and quoted phrases. Must contain 1 to 128 Unicode characters and cannot be all whitespace.
  "count": 10, // The number of results to return, between 1 and 50. Defaults to 10.
  "ori_question": null, // The user's original question that triggered the search, between 1 and 128 characters. Providing it can improve query understanding. `null` is treated as not provided.
  "localization": null, // An optional IP address used to localize search results. Defaults to an empty string.
  "need_content": false, // Whether to return page content in `content`. Defaults to `false`; when `false`, `content` is always an empty string.
}
```

返回结果：
``` json
{
  "static_code": 200, // The static code of the response
  "data": {...} // The data of the response
}
```