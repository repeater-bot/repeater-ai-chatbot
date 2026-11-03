# Workspace Edit Text

同时支持字符偏移、行列，或两者同时提供并校验一致。

注册名：`workspace_edit_text`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `replacement` | string | 必填 | 替换文本；空字符串表示删除 |
| `start_char` | integer | `null` | 0 开始字符偏移 |
| `end_char` | integer | `null` | 结束字符偏移（不含）；null 表示 `start_char` |
| `start_line` | integer | `null` | 1 开始行号 |
| `start_column` | integer | `1` | 1 开始列号 |
| `end_line` | integer | `null` | 结束行号；null 表示 `start_line` |
| `end_column` | integer | `null` | 结束列号（不含） |
| `encoding` | string | `utf-8` | 读写编码 |

至少提供 `start_char` 或 `start_line` 之一。两者都提供时，会先分别换算成字符偏移，不一致直接报错。

## 返回

`mode` 为 `char` / `line` / `both`，并返回 `start_char`、`end_char`、起止行列、`replaced_chars`、`char_count`、`line_count`、`size` 和更新后的 `metadata`。

纯客户端：读取全文后在本地拼接，再调用现有 `write_file` 整体写回。
