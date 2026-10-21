# Workspace Write

把文本内容写入 Data Server 的虚拟工作区。目标路径不存在时，服务器会自动创建文件节点和中间目录。

注册名：`workspace.write`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径，例如 `docs/readme.md` |
| `content` | string | 必填 | 要写入的文本，按 UTF-8 编码后发送 |

```json
{
  "path": "docs/readme.md",
  "content": "hello world"
}
```

## 返回

写入的字节数，作为十进制文本返回，例如：

```text
12
```

## 错误

父路径是文件、目标路径是目录、Data Server 未启动或请求超时等情况，工具会返回文本：

```text
Tool workspace.write error: ...
```

## 说明

- 同名文件会被覆盖，内容以本次写入为准。
- 只能写文本；二进制内容需要先转成 Base64 再由其他工具处理。
- 新建节点时服务器会把索引写回 `index.json`，重启服务后仍可读取。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.write`。详见
[Tool Calls 索引](../index.md)。
