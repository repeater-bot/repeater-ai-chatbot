# Realspace 计算 SHA-256

注册名：`realspace_hash`

## 参数

path: 文件路径；algorithm: 目前只支持 sha256

## 返回

algorithm / digest / size

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `hash` 为 `true`。
`hash` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "hash": true
      }
    ]
  }
}
```
