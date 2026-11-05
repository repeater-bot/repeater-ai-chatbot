# Realspace Read

Read a file from the realspace, optionally a byte range.

注册名：`realspace_read`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The path of the file to read. |
| `content` | `core.tool_caller.tools.realspace_tools.read.Content | core.tool_caller.tools.realspace_tools.read.VarContent` | 必填 | How to return the content: inline, or into a variable. |
| `offset` | `int | None` | `null` | Zero-based byte offset for a partial read. |
| `length` | `int | None` | `null` | Number of bytes to read; null reads to EOF. |

```json
{
  "path": "D:\\Allowed\\example.txt"
}
```

## 返回

文件内容；`var_content` 分支返回写入变量的一行确认信息。

## 错误

失败时工具会返回文本：

```text
Tool realspace_read error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `read` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "read": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_read`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
