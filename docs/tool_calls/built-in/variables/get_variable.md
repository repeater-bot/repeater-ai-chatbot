# Get Variable

读取当前用户某个变量的值。

注册名：`get_variable`（类名 `GetVariable`，实现见 `core/tool_caller/tools/variables/get_variable.py`）

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `variable_name` | string | 必填 | 要读取的变量名 |
| `encoding` | string \| null | `null` | 按该编码把变量里的 `bytes` 解码成文本；非 `bytes` 时不能指定 |

```json
{
  "variable_name": "readme"
}
```

## 返回

- `encoding = null` 且值是 `str` / `bytes`：返回 `repr(值)`。字符串带引号（`'hello'`），
  `bytes` 形如 `b'...'`。
- `encoding = null` 且值是其他类型（`dict` / `list` / `int` / `bool` / `None`）：返回 JSON
  文本，例如 `{"a":1}`、`[1,2]`、`null`，可以直接被解析。
- `encoding` 不为 `null` 且值是 `bytes`：返回按该编码解码后的文本。

## 错误

| 情况 | 工具返回 |
| --- | --- |
| 变量不存在 | `readme is not found.` |
| 指定了 `encoding` 但值不是 `bytes` | `Tool get_variable error: Cannot decode readme(str).` |
| `encoding` 不是合法编码名 | `Tool get_variable error: LookupError: unknown encoding: ...` |

值为 `None` 的变量算存在，读出来是 `null`；这一点与 `variable_exists` 一致。

## 前置条件

本工具**默认不开启**。启用时需要在目标环境的 `configs/project_configs/config.json` 里，
把 `get_variable` 加入 `tool_calls.registed`，并在 `allowed_tool_calls`
（或 `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
以目标环境的实际配置为准。详见 [Tool Calls 索引](../../index.md)。
