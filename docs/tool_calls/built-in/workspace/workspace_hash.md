# Workspace Hash

计算工作区文件的 SHA-256 摘要。

注册名：`workspace_hash`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 文件路径 |
| `algorithm` | string | `sha256` | 目前只支持 SHA-256 |

返回 JSON：`{"algorithm","digest","size"}`。

错误：不支持的算法 400、文件不存在 404、目录 400。

前置条件：`data_server.base_url` 指向运行中的 Data Server，`tool_calls.registed` 包含 `workspace_hash`。
