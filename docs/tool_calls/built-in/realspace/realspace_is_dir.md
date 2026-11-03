# Realspace 判断是否目录

注册名：`realspace_is_dir`

## 参数

path: 路径

## 返回

bool

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `is_dir` 为 `true`。
`is_dir` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "is_dir": true
      }
    ]
  }
}
```
