# Realspace 获取白名单

注册名：`realspace_get_writelist`

## 参数

无参数

## 返回

writelist 的完整条目列表

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `get_writelist` 为 `true`。
`get_writelist` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "get_writelist": true
      }
    ]
  }
}
```
