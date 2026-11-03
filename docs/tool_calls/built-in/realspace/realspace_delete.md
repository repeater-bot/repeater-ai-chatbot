# Realspace 删除文件或目录

注册名：`realspace_delete`

## 参数

path: 文件路径；recursive: 是否递归删除非空目录

## 返回

deleted_files / deleted_dirs

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `delete` 为 `true`。
`delete` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "delete": true
      }
    ]
  }
}
```
