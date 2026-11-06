# Realspace Delete

Delete a file or directory from the realspace. Set recursive=true to delete a non-empty directory.

注册名：`realspace_delete`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | The path of the file or directory to delete. |
| `recursive` | boolean | `false` | Whether to recursively delete the directory and its contents. |

```json
{
  "path": "D:\\Allowed\\example.txt",
  "recursive": false
}
```

## 返回

`deleted_files` / `deleted_dirs`。

## 错误

失败时工具会返回文本：

```text
Tool realspace_delete error: ...
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


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_delete`；`tool_calls.tools_configs.realspace.whitelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
