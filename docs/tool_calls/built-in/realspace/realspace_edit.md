# Realspace 替换字节区间

注册名：`realspace_edit`

## 参数

path: 文件路径；data: Base64 文本；start/end: 半开区间

## 返回

编辑后的文件大小

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `edit` 为 `true`。
`edit` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "edit": true
      }
    ]
  }
}
```
