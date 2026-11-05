# Realspace Edit Text

Edit text by character offsets, line/column, or both; both must resolve to the same range.

注册名：`realspace_edit_text`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The real text file path to edit. |
| `replacement` | string | 必填 | Replacement text; empty string deletes the range. |
| `start_char` | `int | None` | `null` | Zero-based start character offset. |
| `end_char` | `int | None` | `null` | Zero-based end offset; null means start_char. |
| `start_line` | `int | None` | `null` | 1-based start line. |
| `start_column` | integer | `1` | 1-based start column. |
| `end_line` | `int | None` | `null` | 1-based end line; null means start_line. |
| `end_column` | `int | None` | `null` | 1-based end column (exclusive); null means start_column. |
| `encoding` | string | `utf-8` | Text encoding used to read and write the file. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "replacement": "new",
  "start_char": 0,
  "end_char": 5,
  "start_line": 1,
  "start_column": 1,
  "end_line": 1,
  "end_column": 5,
  "encoding": "utf-8"
}
```

## 返回

`TextEditResult` JSON：`mode`、字符区间、行列区间、替换结果和元数据。

## 错误

失败时工具会返回文本：

```text
Tool realspace_edit_text error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `edit_text` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "edit_text": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_edit_text`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
