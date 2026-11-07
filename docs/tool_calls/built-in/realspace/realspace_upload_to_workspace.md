# Realspace Upload To Workspace

从真实路径读取文件字节，上传到 workspace 虚拟路径；源文件不移动、不修改。

注册名：`realspace_upload_to_workspace`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 真实源文件路径，必须位于 realspace whitelist 的读取范围内 |
| `workspace_path` | string \| null | `null` | 目标 workspace 路径；null 使用源文件名 |

```json
{
  "path": "D:\\Allowed\\data.bin",
  "workspace_path": "docs/data.bin"
}
```

## 返回

```json
{
  "source": "D:\\Allowed\\data.bin",
  "destination": "docs/data.bin",
  "size": 12345
}
```

## 白名单

真实路径需要 `realspace.whitelist` 中某个条目的 `path` 覆盖，并且该条目的 `read` 为 `true`；workspace 写入走 Data Server。

## 错误

- 真实路径不在白名单内；
- 源路径是目录或不存在；
- workspace 目标路径非法；
- Data Server 不可用。

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_upload_to_workspace`；`data_server.base_url` 指向运行中的 Data Server。详见
[Tool Calls 索引](../../index.md)。
