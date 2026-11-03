# Realspace glob 匹配

注册名：`realspace_glob`

## 参数

path: 起始目录；pattern: 模式；recursive: 是否递归

## 返回

匹配到的完整路径列表

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `glob` 为 `true`。
`glob` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "glob": true
      }
    ]
  }
}
```
