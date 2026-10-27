# Workspace Exists

检查 Data Server 虚拟工作区中某个路径是否存在。

注册名：`workspace_exists`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要检查的虚拟路径 |

```json
{
  "path": "docs/readme.md"
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

Data Server 无法连接或请求超时等情况，工具会返回文本：

```text
Tool workspace_exists error: ...
```

## 说明

只判断路径是否存在，不读取文件内容，也不会因为路径不存在而报错。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_exists`。详见
[Tool Calls 索引](../../index.md)。
