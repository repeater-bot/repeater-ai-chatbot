# Set Variable

向当前用户的变量表写入一个变量，同名变量会被覆盖。

注册名：`set_variable`（类名 `SetVariable`，实现见 `core/tool_caller/tools/variables/set_variable.py`）

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `variable_name` | string | 必填 | 变量名 |
| `content` | string | 必填 | 要写入的内容 |
| `encoding` | string \| null | `null` | 不为 `null` 时先把 `content` 按该编码转成 `bytes` 再存 |

```json
{
  "variable_name": "readme",
  "content": "hello"
}
```

```json
{
  "variable_name": "blob",
  "content": "5L2g5aW9",
  "encoding": "utf-8"
}
```

## 返回

```text
Set variable finished.
```

## 说明

- 只写**内存**变量表，进程重启后丢失。要落盘必须再调 `dump_variable`。
- `encoding` 为 `null` 时存的是 `str`；指定编码时存的是 `bytes`。后者在 `dump_variable` 时
  无法 JSON 序列化，会导致整份变量都 dump 失败，详见 [Dump Variable](./dump_variable.md)。
- 同名直接覆盖，不做值比较；写入前想查重请用 `variable_exists`。
- 写入过程持有 `ToolsCaller.variable_lock`。

## 错误

| 情况 | 工具返回 |
| --- | --- |
| `encoding` 不是合法编码名 | `Tool set_variable error: LookupError: unknown encoding: ...` |
| `content` 无法用该编码编码（如非 ASCII 字符配 `ascii`） | `Tool set_variable error: UnicodeEncodeError: ...` |
| 缺 `content` 或类型不对 | `Schema validation failed: ...` |

## 前置条件

`configs/project_configs/config.json` 的 `tool_calls.registed` 必须包含 `set_variable`，
用户侧还要在 `allowed_tool_calls`（或 `tool_calls.allowed_by_default`）中允许。详见
[Tool Calls 索引](../index.md)。
