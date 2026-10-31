# Workspace Tree

返回工作区路径的嵌套树。

注册名：`workspace_tree`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 文件或目录路径；根目录传空字符串 |
| `max_depth` | integer | `-1` | `-1` 无限，`0` 只返回根节点 |

节点字段：文件 `{"path","type":"file","size"}`；目录 `{"path","type":"directory","children":[...]}`。

前置条件：`data_server.base_url` 指向运行中的 Data Server，`tool_calls.registed` 包含 `workspace_tree`。
