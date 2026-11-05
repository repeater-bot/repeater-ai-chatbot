# Realspace Get Writelist

Return the configured realspace whitelist entries and their allowed operations.

注册名：`realspace_get_writelist`

## 参数

无参数。

```json
{}
```

## 返回

当前 `writelist` 条目列表，`copy` 以 JSON 名输出。

## 错误

失败时工具会返回文本：

```text
Tool realspace_get_writelist error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

`realspace_get_writelist` 不需要白名单字段；它用于让 AI 先确认当前有哪些路径、每个操作是否开放。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "read": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_get_writelist`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
