# Realspace Copy Range

Copy a byte range of a realspace file into a new file.

注册名：`realspace_copy_range`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The source file path to copy a range from. |
| `destination` | string | 必填 | The destination path of the copied range. |
| `start` | integer | 必填 | Start offset of the copied range. |
| `end` | integer | 必填 | End offset (exclusive) of the copied range. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "destination": "D:\\Allowed\\copy.txt",
  "start": 0,
  "end": 5
}
```

## 返回

`source` / `destination` / `size`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_copy_range error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

白名单位于 `tool_calls.tools_configs.realspace.whitelist`，键是白名单索引，Shell 沙箱也会用这个键选根路径。源路径需要 `read`，目标路径需要 `write`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": {
          "agent": {
            "path": "D:\\Allowed",
            "read": true,
            "write": true
          }
        }
      }
    }
  }
}
```

## 前置条件


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_copy_range`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
