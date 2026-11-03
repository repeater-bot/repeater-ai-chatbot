# Workspace Edit Text By Char

按绝对字符偏移替换文本。

注册名：`workspace_edit_text_by_char`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `replacement` | string | 必填 | 替换文本；空字符串删除 |
| `start` | integer | 必填 | 0 开始字符偏移 |
| `end` | integer | `null` | 结束偏移（不含）；null 表示 `start` |
| `encoding` | string | `utf-8` | 读写编码 |

返回 `mode="char"`、起止字符偏移、换算后的行列和元数据。

```python
workspace_edit_text_by_char(
    path="docs/a.txt",
    replacement="TWO",
    start=4,
    end=7
)
```
