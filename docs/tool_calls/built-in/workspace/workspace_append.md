# Workspace Append

向 Data Server 虚拟工作区文件追加字节；文件不存在时自动创建。

注册名：`workspace_append`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 目标文件路径 |
| `data` | string | 必填 | 要追加的 Base64 文本 |

```json
{
  "path": "logs/app.log",
  "data": "aGVsbG8K"
}
```

## 返回

追加后的文件大小（字节），作为十进制文本返回：

```text
6
```

## 错误

以下情况会返回文本：

```text
Tool workspace_append error: ...
```

- 目标是目录；
- 父路径是文件；
- `data` 不是合法 Base64；
- Data Server 无法连接或请求超时。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_append`。详见
[Tool Calls 索引](../../index.md)。
