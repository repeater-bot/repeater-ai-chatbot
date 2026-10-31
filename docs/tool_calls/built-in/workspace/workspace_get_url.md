# Workspace Get Url

返回工作区文件的读取 URL。

注册名：`workspace_get_url`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 文件路径 |

返回形如 `http://<data-server>/operations/read/<path>` 的 URL 文本，不读取文件内容。

前置条件：`data_server.base_url` 指向运行中的 Data Server，`tool_calls.registed` 包含 `workspace_get_url`。
