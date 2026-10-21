# Workspace Delete

删除 Data Server 虚拟工作区中的文件或空目录。

注册名：`workspace.delete`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要删除的虚拟文件或目录路径 |

```json
{
  "path": "docs/readme.md"
}
```

## 返回

删除结果，JSON 对象：

```json
{
  "deleted_files": 1,
  "deleted_dirs": 0
}
```

`deleted_files` 是删除的文件数，`deleted_dirs` 是删除的目录数
（删除文件时为 0，删除空目录时为 1）。

## 错误

以下情况会返回文本：

```text
Tool workspace.delete error: ...
```

- 路径不存在（服务器 404）；
- `path` 为空（客户端直接拒绝；直接调用 API 时服务器对根目录返回 403）；
- 目标是非空目录（服务器 409）；
- Data Server 未启动或请求超时。

## 说明

当前工具只暴露 `path`，**没有 `recursive` 参数**，因此只能删除文件或空目录。
需要递归删除时，要么先逐个删除子项，要么扩展本工具的参数后调用
`DataClient.delete(path, recursive=True)`。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.delete`。详见
[Tool Calls 索引](../index.md)。
