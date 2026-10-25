# Workspace List

列出 Data Server 虚拟工作区中某个目录的直接子项名称。

注册名：`workspace_list`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟目录路径；根目录传空字符串 `""` |

```json
{
  "path": "docs"
}
```

根目录：

```json
{
  "path": ""
}
```

## 返回

子项名称的 JSON 数组，按索引中的顺序返回：

```json
[
  "readme.md",
  "images"
]
```

返回值只包含直接子项，不会递归展开。

## 错误

路径不存在、路径是文件、Data Server 未启动或请求超时等情况，工具会返回文本：

```text
Tool workspace.list error: ...
```

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.list`。详见
[Tool Calls 索引](../index.md)。
