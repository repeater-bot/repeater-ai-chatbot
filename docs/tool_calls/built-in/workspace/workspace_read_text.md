# Workspace Read Text

读取文本文件，并在客户端完成分行、行号和字符偏移计算。

注册名：`workspace_read_text`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `encoding` | string | `utf-8` | 解码编码 |

## 返回

```json
{
  "content": "one\ntwo\n",
  "numbered_content": "   1 | one\n   2 | two\n",
  "lines": [
    {
      "number": 1,
      "start": 0,
      "end": 3,
      "raw_end": 4,
      "text": "one",
      "ending": "\n"
    }
  ],
  "metadata": {
    "path": "docs/a.txt",
    "encoding": "utf-8",
    "byte_size": 8,
    "char_count": 8,
    "line_count": 2,
    "newline": "\n",
    "st_mtime": 0.0,
    "st_mode": "0o100644"
  }
}
```

- 行号从 1 开始；
- `start` / `end` / `raw_end` 是整段文本中的字符偏移，`end` 不含换行符；
- 分行、行号和元数据都在客户端算，不调用新的服务端接口。
