# Realspace 获取文件 URL

注册名：`realspace_get_url`

## 参数

path: 文件路径

## 返回

file:// URL

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `get_url` 为 `true`。
`get_url` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "get_url": true
      }
    ]
  }
}
```
