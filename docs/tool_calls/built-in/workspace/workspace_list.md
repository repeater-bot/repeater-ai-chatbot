# Workspace List

列出 Data Server 虚拟工作区中某个目录的子项路径。

注册名：`workspace_list`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟目录路径；根目录传空字符串 `""` |
| `recursive` | boolean | `false` | 为 `true` 时递归列出所有后代路径，否则只列直接子项 |

直接子项：

```json
{
  "path": "docs",
  "recursive": false
}
```

递归：

```json
{
  "path": "docs",
  "recursive": true
}
```

## 返回

完整虚拟路径的 JSON 数组，文件和目录都包含：

```json
[
  "docs/a.md",
  "docs/sub"
]
```

`recursive = true` 时会展开到所有后代：

```json
[
  "docs/a.md",
  "docs/sub",
  "docs/sub/c.md"
]
```

## 错误

路径不存在、路径是文件、Data Server 无法连接或请求超时等情况，工具会返回文本：

```text
Tool workspace_list error: ...
```

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_list`。详见
[Tool Calls 索引](../../index.md)。
