# Workspace Read

从 Data Server 的虚拟工作区读取文件内容。

注册名：`workspace.read`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径，相对于 Data Server 的 `base_path`，例如 `docs/readme.md` |
| `base64_encode` | boolean | `false` | 是否把原始字节做 Base64 编码后返回 |

```json
{
  "path": "docs/readme.md",
  "base64_encode": false
}
```

## 返回

- `base64_encode = false`：UTF-8 文本内容。
- `base64_encode = true`：Base64 字符串，适合图片、压缩包等二进制文件。

## 错误

文件不存在、路径是目录、Data Server 未启动或请求超时等情况，工具会返回文本：

```text
Tool workspace.read error: ...
```

读取非 UTF-8 的二进制文件时请设置 `base64_encode = true`；否则 UTF-8 解码失败也会走上面的错误路径。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.read`。详见
[Tool Calls 索引](../index.md)。
