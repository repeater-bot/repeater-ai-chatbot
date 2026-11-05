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

需要 `tool_calls.tools_configs.realspace.writelist` 中某个条目的 `path` 覆盖目标路径，并且该条目的 `delete` 为 `true`。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "writelist": [
          {
            "path": "D:\\Allowed",
            "delete": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_delete`；`tool_calls.tools_configs.realspace.writelist` 中至少有一个条目覆盖目标路径。详见
[Tool Calls 索引](../../index.md)。
