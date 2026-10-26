# Workspace Delete

删除 Data Server 虚拟工作区中的文件或目录。

注册名：`workspace_delete`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要删除的虚拟文件或目录路径 |
| `recursive` | boolean | `false` | 删除非空目录时必须设为 `true`，会连同所有子项一起删除 |

```json
{
  "path": "docs",
  "recursive": true
}
```

## 返回

删除结果，JSON 对象：

```json
{
  "deleted_files": 12,
  "deleted_dirs": 3
}
```

`deleted_files` 是删除的文件数，`deleted_dirs` 是删除的目录数。
递归删除时，两者都包含所有后代，目录数还包含目标目录本身。

## 错误

以下情况会返回文本：

```text
Tool workspace_delete error: ...
```

- 路径不存在（服务器 404）；
- `path` 为空（客户端直接拒绝；直接调用 API 时服务器对根目录返回 403）；
- 非空目录且 `recursive = false`（服务器 409）；
- Data Server 无法连接或请求超时。

## 说明

- `recursive = false` 只能删除文件或空目录；
- `recursive = true` 会删除目标目录及其下所有文件和子目录；
- 删除会同时移除索引节点和对应的数据文件。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_delete`。详见
[Tool Calls 索引](../../index.md)。
