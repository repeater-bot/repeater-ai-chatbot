# Realspace 复制字节区间

注册名：`realspace_copy_range`

## 参数

path: 源文件；destination: 新文件；start/end: 半开区间

## 返回

source / destination / size

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `copy_range` 为 `true`。
`copy_range` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "copy_range": true
      }
    ]
  }
}
```
