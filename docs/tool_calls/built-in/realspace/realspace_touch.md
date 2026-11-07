# Realspace Touch

Create an empty realspace file when missing, or refresh its timestamp.

注册名：`realspace_touch`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The file path to create or touch. |

```json
{
  "path": "D:\\Allowed\\example.txt"
}
```

## 返回

当前文件大小；新建时为 `0`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_touch error: ...
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


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_touch`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
