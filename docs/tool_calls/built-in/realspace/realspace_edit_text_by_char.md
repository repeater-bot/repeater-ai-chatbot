# Realspace Edit Text By Char

Replace a text range by absolute character offsets, reading and writing the whole file.

注册名：`realspace_edit_text_by_char`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The real text file path to edit. |
| `replacement` | string | 必填 | Replacement text; empty string deletes the range. |
| `start` | integer | 必填 | Zero-based start character offset. |
| `end` | `int | None` | `null` | Zero-based end offset; null means start. |
| `encoding` | string | `utf-8` | Text encoding used to read and write the file. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "replacement": "new",
  "start": 0,
  "end": 5,
  "encoding": "utf-8"
}
```

## 返回

`TextEditResult` JSON，`mode = "char"`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_edit_text_by_char error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `edit_text_by_char` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "edit_text_by_char": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_edit_text_by_char`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
