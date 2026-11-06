# Realspace Edit

Replace a byte range in a realspace file with Base64-encoded bytes.

注册名：`realspace_edit`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The file path to edit. |
| `data` | string | 必填 | Base64-encoded replacement bytes. |
| `start` | integer | 必填 | Start offset of the replaced range. |
| `end` | integer | 必填 | End offset (exclusive) of the replaced range. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "data": "aGVsbG8=",
  "start": 0,
  "end": 5
}
```

## 返回

编辑后的文件大小。

## 错误

失败时工具会返回文本：

```text
Tool realspace_edit error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

白名单位于 `tool_calls.tools_configs.realspace.whitelist`，键是白名单索引，Shell 沙箱也会用这个键选根路径。需要该条目的 `write` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": {
          "agent": {
            "path": "D:\\Allowed",
            "read": false,
            "write": true
          }
        }
      }
    }
  }
}
```

## 前置条件


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_edit`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
