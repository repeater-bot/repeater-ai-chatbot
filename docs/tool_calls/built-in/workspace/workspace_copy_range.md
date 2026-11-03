# Workspace Copy Range

把源文件的一段字节复制成新文件。

注册名：`workspace_copy_range`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 源文件路径 |
| `destination` | string | 必填 | 新文件路径 |
| `start` | integer | 必填 | 起始偏移，`>= 0` |
| `end` | integer | 必填 | 结束偏移（不含），`>= start` |

返回 JSON：`{"source","destination","size"}`。

目标必须不存在；源不存在 404、目标已存在 409、区间非法 400。

前置条件：`data_server.base_url` 指向运行中的 Data Server，`tool_calls.registed` 包含 `workspace_copy_range`。
