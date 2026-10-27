# Workspace Glob

在 Data Server 虚拟工作区中按 glob 模式扫描路径。

注册名：`workspace_glob`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | `""` | 扫描的起始目录；空字符串表示工作区根目录 |
| `pattern` | string | 必填 | glob 模式，例如 `*.md`、`sub/*.md`、`**/*.md` |
| `recursive` | boolean | `false` | 为 `true` 时在 `path` 下任意深度匹配，等价于 `**/<pattern>` |

```json
{
  "path": "docs",
  "pattern": "*.md",
  "recursive": true
}
```

匹配规则：

- `*` / `?` / `[...]` 只匹配单个路径段；
- `**` 可以跨任意层目录；
- 裸模式（不含 `/` 和 `**`）只匹配起始目录的直接子项；
- `recursive = true` 时自动按 `**/<pattern>` 递归匹配。

## 返回

完整虚拟路径的 JSON 数组，文件和目录都可能包含：

```json
[
  "docs/a.md",
  "docs/sub/c.md"
]
```

## 错误

起始路径不存在、起始路径是文件、`pattern` 为空、Data Server 无法连接或请求超时等情况，
工具会返回文本：

```text
Tool workspace_glob error: ...
```

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_glob`。详见
[Tool Calls 索引](../../index.md)。
