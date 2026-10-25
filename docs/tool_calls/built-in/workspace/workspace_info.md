# Workspace Info

获取 Data Server 虚拟工作区中一个文件的元信息。

注册名：`workspace_info`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径，例如 `docs/readme.md` |

```json
{
  "path": "docs/readme.md"
}
```

## 返回

文件元信息的 JSON 对象：

```json
{
  "size": 12345,
  "st_mtime": 1792297108.85,
  "st_mtime_ns": 1792297108853883900,
  "st_atime": 1792297109.40,
  "st_atime_ns": 1792297109400950700,
  "st_mode": "0b1000000110110110"
}
```

| 字段 | 说明 |
| --- | --- |
| `size` | 文件大小，单位字节 |
| `st_mtime` / `st_mtime_ns` | 最后修改时间（秒 / 纳秒时间戳） |
| `st_atime` / `st_atime_ns` | 最后访问时间（秒 / 纳秒时间戳） |
| `st_mode` | 权限位，`os.stat().st_mode` 的二进制字符串 |

## 错误

路径不存在、路径是目录、Data Server 未启动或请求超时等情况，工具会返回文本：

```text
Tool workspace.info error: ...
```

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.info`。详见
[Tool Calls 索引](../index.md)。
