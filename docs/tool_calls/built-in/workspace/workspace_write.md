# Workspace Write

把文本内容写入 Data Server 的虚拟工作区。目标路径不存在时，服务器会自动创建文件节点和中间目录。

注册名：`workspace_write`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径，例如 `docs/readme.md` |
| `content` | object | 必填 | 写入方式，二选一：`content`（直接给文本）或 `var_content`（从变量取） |

`content` 分支：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `content` | string | 必填 | 要写入的文本 |
| `encoding` | string | `utf-8` | 把文本编码成字节用的编码 |

`var_content` 分支：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `var_name` | string | 必填 | 来源变量名 |
| `encoding` | string \| null | `null` | 变量是 `str` 时用这个编码转成字节；`null` 按 `utf-8` 处理 |
| `base64_encode` | boolean | `false` | 变量里是 Base64 文本，写入前先解码成原始字节 |

从变量读取并写入：
```json
{
  "path": "docs/readme.md",
  "content": {
    "type": "var_content",
    "var_name": "readme",
    "encoding": null,
    "base64_encode": false
  }
}
```

直接写入：
```json
{
  "path": "docs/readme.md",
  "content": {
    "type": "content",
    "content": "hello world",
    "base64_encode": false,
    "encoding": "utf-8"
  }
}
```

## 从变量写入时取什么字节

| 变量类型 / 参数 | 实际写入文件的内容 |
| --- | --- |
| 变量是 `bytes`、`base64_encode = false` | 这些原始字节 |
| 变量是 `str`、`base64_encode = false` | `变量.encode(encoding)`，`encoding` 缺省 `utf-8` |
| `base64_encode = true` | 先把变量文本按 Base64 解码，再写解码后的字节 |

变量不存在时不会写信内容，返回：

```text
Tool workspace_write error: 'Variable readme not found'
```

`base64_encode = true` 但内容不是合法 Base64 时同样直接报错，不会写入半截数据。

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
- 二进制内容建议走 `workspace_read`（`base64_encode = true`）→ `workspace_write`
  （`base64_encode = true`）这条往返路径，Base64 文本是可持久化的 `str`。
- `workspace_read` 用 `encoding = null` 存进变量的原始 `bytes` 也能被写入，但这类变量
  无法被 `dump_variable` 持久化，详见 [Dump Variable](../variables/dump_variable.md)。
- 新建节点时服务器会把索引写回 `index.json`，重启服务后仍可读取。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace.write`。详见
[Tool Calls 索引](../index.md)。
