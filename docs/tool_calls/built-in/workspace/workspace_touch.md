# Workspace Touch

创建工作区空文件，或刷新已有文件的修改时间。

注册名：`workspace_touch`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |

```json
{
  "path": "docs/new.bin"
}
```

## 返回

当前文件大小，作为十进制文本返回：

```text
0
```

## 说明

- 文件不存在时创建空文件（自动补齐父目录）；
- 文件已存在时**不清空内容**，只刷新 mtime；
- 目标是目录时返回错误。

## 错误

以下情况会返回文本：

```text
Tool workspace_touch error: ...
```

- 目标是目录（400）；
- 父路径是文件（400）；
- Data Server 无法连接或请求超时。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_touch`。详见
[Tool Calls 索引](../../index.md)。
