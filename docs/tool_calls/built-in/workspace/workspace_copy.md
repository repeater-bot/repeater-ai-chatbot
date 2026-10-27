# Workspace Copy

复制 Data Server 虚拟工作区中的文件或目录。目录会被递归克隆，每个文件都分配新的文件 ID
并复制一份 payload；源文件和目录保持不变。

注册名：`workspace_copy`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 当前虚拟路径，例如 `docs` |
| `destination` | string | 必填 | 目标虚拟路径（包含新名称，不是目标目录），例如 `backup/docs` |

```json
{
  "path": "docs",
  "destination": "backup/docs"
}
```

## 返回

复制结果，JSON 对象：

```json
{
  "source": "docs",
  "destination": "backup/docs",
  "copied_files": 12,
  "copied_dirs": 3
}
```

| 字段 | 说明 |
| --- | --- |
| `source` / `destination` | 规范化后的源路径和目标路径 |
| `copied_files` | 复制出的文件数 |
| `copied_dirs` | 新建的目录节点数；复制目录时包含目标目录本身，复制单个文件时为 `0` |

## 错误

以下情况会返回文本：

```text
Tool workspace_copy error: ...
```

- `path` 为空（工作区根目录）或 `destination` 为空（服务器 403）；
- 源路径不存在（服务器 404）；
- `destination` 已存在（服务器 409），包括 `destination` 与 `path` 相同；
- `destination` 的某个已存在父级是文件（服务器 400）；
- 把目录复制到它自己的子目录下（服务器 403）；
- Data Server 无法连接或请求超时。

## 说明

- 复制目录会递归复制所有后代，源文件内容不变；
- 每个新文件的 ID 与源文件不同，payload 是独立副本；
- `destination` 的父目录不存在时会自动创建；
- 目标已存在时不会覆盖，也不会与已有目录合并；
- payload 复制失败时不会改动索引，已经写出的半成品 payload 会被清理。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_copy`。详见
[Tool Calls 索引](../../index.md)。
