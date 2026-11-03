# Realspace 复制文件或目录

注册名：`realspace_copy`

## 参数

path: 源路径；destination: 目标路径

## 返回

source / destination / copied_files / copied_dirs

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `copy_` 为 `true`。
`copy_` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "copy_": true
      }
    ]
  }
}
```
