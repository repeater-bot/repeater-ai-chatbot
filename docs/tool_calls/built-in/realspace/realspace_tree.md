# Realspace Tree

Return the nested node tree below a realspace path.

注册名：`realspace_tree`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The realspace path to walk (an empty string walks the root). |
| `max_depth` | integer | `-1` | Maximum depth of the returned tree; -1 means unlimited. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "max_depth": -1
}
```

## 返回

嵌套的 `path` / `type` / `size` 或 `children`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_tree error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `tree` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "tree": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_tree`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
