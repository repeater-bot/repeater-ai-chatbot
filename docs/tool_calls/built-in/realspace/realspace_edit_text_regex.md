# Realspace Edit Text Regex

Scan text with a regular expression, replace matches, and write the whole file back; no match errors.

注册名：`realspace_edit_text_regex`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The real text file path to edit. |
| `pattern` | string | 必填 | Regular expression used to scan the text. |
| `replacement` | string | 必填 | re.sub replacement; supports backreferences like \1. |
| `count` | integer | `1` | Number of matches to replace; 0 means all. |
| `ignore_case` | boolean | `false` | Case-insensitive matching. |
| `multiline` | boolean | `false` | Make ^ and $ match line boundaries. |
| `dotall` | boolean | `false` | Make . match newlines. |
| `encoding` | string | `utf-8` | Text encoding used to read and write the file. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "pattern": "old",
  "replacement": "new",
  "count": 1,
  "ignore_case": false,
  "multiline": false,
  "dotall": false,
  "encoding": "utf-8"
}
```

## 返回

`TextRegexEditResult` JSON：替换数量、匹配位置和元数据。

## 错误

失败时工具会返回文本：

```text
Tool realspace_edit_text_regex error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `edit_text_regex` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "edit_text_regex": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_edit_text_regex`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
