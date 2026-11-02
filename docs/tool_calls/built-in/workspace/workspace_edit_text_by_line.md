# Workspace Edit Text By Line

按 1 开始的行列替换文本。

注册名：`workspace_edit_text_by_line`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `replacement` | string | 必填 | 替换文本；空字符串删除 |
| `start_line` | integer | `1` | 起始行 |
| `start_column` | integer | `1` | 起始列 |
| `end_line` | integer | `null` | 结束行；null 表示 `start_line` |
| `end_column` | integer | `null` | 结束列（不含） |
| `encoding` | string | `utf-8` | 读写编码 |

`column` 可为行内容长度 + 1，表示换行符之前；`line = 行数 + 1, column = 1` 表示 EOF。

返回 `mode="line"`、起止行列、换算后的字符偏移和元数据。

```python
workspace_edit_text_by_line(
    path="docs/a.txt",
    replacement="TWO",
    start_line=2,
    start_column=1,
    end_line=2,
    end_column=4
)
```
