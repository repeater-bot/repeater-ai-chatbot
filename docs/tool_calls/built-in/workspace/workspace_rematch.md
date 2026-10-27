# Workspace Rematch

用正则表达式匹配 Data Server 虚拟工作区中的单条路径。

注册名：`workspace_rematch`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要匹配的虚拟路径 |
| `pattern` | string | 必填 | Python 正则表达式，使用 `re.match` 从路径开头匹配 |

```json
{
  "path": "docs/readme.md",
  "pattern": ".*\\.md$"
}
```

## 返回

布尔值，作为文本返回：

```text
true
```

或：

```text
false
```

## 错误

`pattern` 为空、正则表达式非法、Data Server 无法连接或请求超时等情况，
工具会返回文本：

```text
Tool workspace_rematch error: ...
```

## 说明

只做字符串匹配，**不检查路径是否真实存在**；要判断存在性请用 `workspace_exists`。
因为使用 `re.match`，模式从路径开头匹配；要匹配后缀可以写成 `.*\.md$`。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_rematch`。详见
[Tool Calls 索引](../../index.md)。
