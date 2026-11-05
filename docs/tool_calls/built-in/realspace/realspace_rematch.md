# Realspace Rematch

Check whether a virtual realspace path matches a regular expression.

注册名：`realspace_rematch`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The virtual path to match. |
| `pattern` | string | 必填 | Python regular expression; re.match is used from the start of the path. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "pattern": "old"
}
```

## 返回

布尔值。

## 错误

失败时工具会返回文本：

```text
Tool realspace_rematch error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `rematch` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "rematch": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_rematch`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
