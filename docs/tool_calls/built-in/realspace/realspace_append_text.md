# Realspace Append Text

Append text to a realspace file, creating it if missing.

注册名：`realspace_append_text`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The file path to append to. |
| `text` | string | 必填 | Text to append. |
| `encoding` | string | `utf-8` | Encoding of the text. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "text": "hello",
  "encoding": "utf-8"
}
```

## 返回

追加后的文件大小。

## 错误

失败时工具会返回文本：

```text
Tool realspace_append_text error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `append_text` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "append_text": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_append_text`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
