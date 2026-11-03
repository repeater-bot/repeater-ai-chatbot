# Realspace 移动/重命名

注册名：`realspace_move`

## 参数

path: 源路径；destination: 目标路径

## 返回

source / destination

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `move` 为 `true`。
`move` 是去掉 `realspace_` 前缀后的工具名；`copy` 在 Python 字段中写作 `copy_`，配置里仍是 `copy`。

```json
{
  "realspace": {
    "writelist": [
      {
        "path": "D:\\Allowed",
        "move": true
      }
    ]
  }
}
```
