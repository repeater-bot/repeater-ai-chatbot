# Realspace 创建目录

注册名：`realspace_mkdir`

## 参数

path: 目录路径，自动补齐父目录

## 返回

创建的目录路径

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `mkdir` 为 `true`。
`mkdir` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "mkdir": true
      }
    ]
  }
}
```
