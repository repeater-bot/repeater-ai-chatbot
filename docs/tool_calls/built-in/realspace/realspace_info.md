# Realspace 读取元数据

注册名：`realspace_info`

## 参数

path: 路径

## 返回

size / mtime / atime / mode

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `info` 为 `true`。
`info` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "info": true
      }
    ]
  }
}
```
