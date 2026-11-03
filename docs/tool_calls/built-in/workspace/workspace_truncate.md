# Workspace Truncate

把已有 Data Server 虚拟工作区文件调整为指定字节数。

注册名：`workspace_truncate`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `size` | integer | 必填 | 目标字节数，必须 `>= 0` |

```json
{
  "path": "docs/a.bin",
  "size": 1024
}
```

## 返回

调整后的文件大小，作为十进制文本返回：

```text
1024
```

## 说明

- 缩短会截断尾部；
- 扩大用零字节补齐；
- 文件必须已存在（不存在返回 404）。

## 错误

以下情况会返回文本：

```text
Tool workspace_truncate error: ...
```

- 文件不存在（404）；
- 目标是目录（400）；
- `size` 为负数（400）；
- Data Server 无法连接或请求超时。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_truncate`。详见
[Tool Calls 索引](../../index.md)。
