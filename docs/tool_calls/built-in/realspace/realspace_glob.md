# Realspace Glob

List realspace paths matching a glob pattern below a directory.

注册名：`realspace_glob`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | `` | The virtual directory to scan; an empty string means the realspace root. |
| `pattern` | string | 必填 | Glob pattern, for example '*.md', 'sub/*.md' or '**/*.md'. |
| `recursive` | boolean | `false` | Whether to match the pattern at any depth below the directory. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "pattern": "old",
  "recursive": false
}
```

## 返回

匹配到的完整路径列表。

## 错误

失败时工具会返回文本：

```text
Tool realspace_glob error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `glob` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "glob": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_glob`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
