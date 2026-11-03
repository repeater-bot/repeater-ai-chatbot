# Realspace 返回嵌套树

注册名：`realspace_tree`

## 参数

path: 文件或目录路径；max_depth: -1 表示无限

## 返回

path / type / size 或 children

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `tree` 为 `true`。
`tree` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "tree": true
      }
    ]
  }
}
```
