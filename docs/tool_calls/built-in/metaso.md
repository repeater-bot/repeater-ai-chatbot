# Metaso

Metaso 用于快速进行互联网搜索并进行 AI 总结
使用它你需要配置环境变量 `METASO_API_KEY`

注册名：`metaso`

接受六个参数：
``` json
{
  "q": "", // The query to search for
  "scope": "webpage", // The scope to search in
  "includeSummary": false, // Whether to include a summary of the results
  "size": "10", // The number of results to return
  "includeRawContent": false, // Whether to include the raw content of the results
  "conciseSnippet": false, // Whether to include a concise snippet of the results
}
```

返回结果：
``` json
{
  "static_code": 200, // The static code of the response
  "data": {...} // The data of the response
}
```