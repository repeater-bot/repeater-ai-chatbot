# Realspace 创建空文件或刷新 mtime

注册名：`realspace_touch`

## 参数

path: 文件路径

## 返回

当前文件大小

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `touch` 为 `true`。
`touch` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "touch": true
      }
    ]
  }
}
```
