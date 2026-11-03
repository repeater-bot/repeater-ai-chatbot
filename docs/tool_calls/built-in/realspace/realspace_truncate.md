# Realspace 调整文件大小

注册名：`realspace_truncate`

## 参数

path: 文件路径；size: 目标字节数

## 返回

最终大小

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `truncate` 为 `true`。
`truncate` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "truncate": true
      }
    ]
  }
}
```
