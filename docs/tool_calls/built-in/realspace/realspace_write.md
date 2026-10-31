# Realspace 写入文件

注册名：`realspace_write`

## 参数

path: 文件路径；content: 文本内容或变量内容

## 返回

写入的字节数

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `write` 为 `true`。
`write` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "write": true
      }
    ]
  }
}
```
