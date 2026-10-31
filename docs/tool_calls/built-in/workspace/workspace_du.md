# Workspace Du

统计工作区路径的总字节数、文件数和目录数。

注册名：`workspace_du`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 文件或目录路径；根目录传空字符串 |

返回 JSON：`{"path","size","files","dirs"}`。`dirs` 包含目标目录自身；文件为 `files=1, dirs=0`。

前置条件：`data_server.base_url` 指向运行中的 Data Server，`tool_calls.registed` 包含 `workspace_du`。
