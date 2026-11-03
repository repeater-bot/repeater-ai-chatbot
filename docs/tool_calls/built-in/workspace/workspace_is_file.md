# Workspace Is File

判断 Data Server 虚拟工作区中的路径是不是文件。

注册名：`workspace_is_file`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要判断的虚拟路径 |

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

## 说明

路径不存在、路径是目录都返回 `false`，不会报错；只做类型判断，不读取内容。

## 错误

Data Server 无法连接或请求超时等情况，工具会返回文本：

```text
Tool workspace_is_file error: ...
```

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_is_file`。详见
[Tool Calls 索引](../../index.md)。
