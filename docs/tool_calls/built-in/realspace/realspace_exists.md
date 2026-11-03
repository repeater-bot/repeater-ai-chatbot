# Realspace 判断路径是否存在

注册名：`realspace_exists`

## 参数

path: 文件或目录路径

## 返回

bool

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `exists` 为 `true`。
`exists` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "exists": true
      }
    ]
  }
}
```
