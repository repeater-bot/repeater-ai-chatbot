# Realspace Info

Info about the realspace item.

注册名：`realspace_info`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The destination path to get metadata from. |

```json
{
  "path": "D:\\Allowed\\example.txt"
}
```

## 返回

`size`、`st_mtime`、`st_atime`、`st_mode` 等元数据。

## 错误

失败时工具会返回文本：

```text
Tool realspace_info error: ...
```

常见原因包括路径不在白名单、路径为空、目标不存在、目标已存在、区间非法，或本地文件系统拒绝访问。

## 白名单

需要 `tool_calls.tools_configs.realspace.whitelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `info` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": [
          {
            "path": "D:\\Allowed",
            "info": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_info`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
