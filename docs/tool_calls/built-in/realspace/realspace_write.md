# Realspace Write

Write text to a realspace file, creating it if missing. Returns the number of bytes written.

注册名：`realspace_write`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The path of the file to write. |
| `content` | `core.tool_caller.tools.realspace_tools.write.Content | core.tool_caller.tools.realspace_tools.write.VarContent` | 必填 | The content to write to the file. |

```json
{
  "path": "D:\\Allowed\\example.txt"
}
```

## 返回

写入的字节数。

## 错误

失败时工具会返回文本：

```text
Tool realspace_write error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

白名单位于 `tool_calls.tools_configs.realspace.whitelist`，键是白名单索引，Shell 沙箱也会用这个键选根路径。需要该条目的 `write` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": {
          "agent": {
            "path": "D:\\Allowed",
            "read": false,
            "write": true
          }
        }
      }
    }
  }
}
```

## 前置条件


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_write`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
