# Workspace Edit Text Regex

用正则扫描整段文本，替换后整体写回。找不到匹配会直接报错，不会意外写回原文件。

注册名：`workspace_edit_text_regex`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `pattern` | string | 必填 | 正则表达式 |
| `replacement` | string | 必填 | `re.sub` 替换文本，支持 `\1` 反向引用 |
| `count` | integer | `1` | 替换次数；`0` 表示全部 |
| `ignore_case` | bool | `false` | 忽略大小写 |
| `multiline` | bool | `false` | `^` / `$` 匹配行边界 |
| `dotall` | bool | `false` | `.` 匹配换行 |
| `encoding` | string | `utf-8` | 读写编码 |

## 行为

1. 读取全文；
2. `re.finditer` 扫描；
3. 没有匹配 → `ValueError("regular expression did not match the file")`；
4. 有匹配 → `re.sub` 替换，整体写回；
5. 返回替换数量、每个匹配的原始位置和行列。

## 返回

```json
{
  "path": "docs/a.txt",
  "pattern": "two",
  "replacement": "TWO",
  "requested_count": 1,
  "replaced": 1,
  "matches": [
    {
      "start": 4,
      "end": 7,
      "text": "two",
      "start_line": 2,
      "start_column": 1,
      "end_line": 2,
      "end_column": 4
    }
  ],
  "char_count": 14,
  "line_count": 4,
  "size": 14
}
```

`matches` 记录的是替换前的位置；`count` 大于实际匹配数时只替换实际匹配。
