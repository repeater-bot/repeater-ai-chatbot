# Realspace 读取文件

注册名：`realspace_read`

## 参数

path: 文件路径；content: inline 内容或写入变量；offset/length: 可选字节区间

## 返回

文本/字节，或写入变量的确认信息

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `read` 为 `true`。
`read` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "read": true
      }
    ]
  }
}
```
