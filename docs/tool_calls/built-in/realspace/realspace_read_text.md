# Realspace Read Text

Read a real text file with numbered lines, character offsets and metadata.

注册名：`realspace_read_text`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The real text file path to read. |
| `encoding` | string | `utf-8` | Text encoding used to decode the file. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "encoding": "utf-8"
}
```

## 返回

`TextFile` JSON：`content`、`numbered_content`、`lines`、`metadata`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_read_text error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `read_text` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "read_text": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_read_text`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
