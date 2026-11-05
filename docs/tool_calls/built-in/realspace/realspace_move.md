# Realspace Move

Move a file or directory in the realspace; file ids and payloads stay unchanged.

注册名：`realspace_move`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The current path of the file or directory. |
| `destination` | string | 必填 | The new virtual path. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "destination": "D:\\Allowed\\copy.txt"
}
```

## 返回

`source` / `destination`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_move error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `move` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "move": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_move`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
