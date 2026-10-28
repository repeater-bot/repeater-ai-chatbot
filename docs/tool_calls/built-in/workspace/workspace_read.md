# Workspace Read

从 Data Server 的虚拟工作区读取文件内容。

注册名：`workspace_read`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径，相对于 Data Server 的 `base_path`，例如 `docs/readme.md` |
| `content` | object | 必填 | 取回方式，二选一：`content`（直接返回文本）或 `var_content`（存进变量） |
| `offset` | integer \| null | `null` | 可选，从 0 开始的字节偏移；`null` 从文件开头读 |
| `length` | integer \| null | `null` | 可选，读取字节数；`null` 读到 EOF |

`offset` / `length` 作用于**原始字节**，在解码或 Base64 编码之前完成。
例如只读取前 1 KiB：

```json
{
  "path": "docs/big.bin",
  "offset": 0,
  "length": 1024,
  "content": {
    "type": "content",
    "base64_encode": true,
    "encoding": "utf-8"
  }
}
```

`content` 分支：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `base64_encode` | boolean | `false` | 是否把原始字节做 Base64 编码后返回 |
| `encoding` | string | `utf-8` | 解码文件内容用的编码 |

`var_content` 分支：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `var_name` | string | 必填 | 接收文件内容的变量名 |
| `encoding` | string \| null | `null` | 解码文件内容用的编码；`null` 表示变量直接存原始 `bytes` |
| `base64_encode` | boolean | `false` | 是否先做 Base64 编码再存进变量 |

写入变量：
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

直接读取：
```json
{
  "path": "docs/readme.md",
  "content": {
    "type": "content",
    "base64_encode": false,
    "encoding": "utf-8"
  }
}
```

## 变量里存成什么类型

| 参数组合 | 变量类型 |
| --- | --- |
| `encoding = null`、`base64_encode = false` | `bytes`（原始字节；**无法被 `dump_variable` 持久化**） |
| `encoding` 有值、`base64_encode = false` | `str`（按该编码解码后的文本） |
| `base64_encode = true` | `str`（Base64 文本；`encoding` 缺省按 `utf-8` 解码 Base64 文本本身，不影响文件字节） |

想让它能落盘，就别用 `encoding = null`；这条路径上存进去的 `bytes` 会让整份变量 dump 失败，
详见 [Dump Variable](../variables/dump_variable.md)。

## 返回

- `content`：文件内容，直接作为文本返回。
- `var_content`：不返回文件内容，返回一行确认信息，括号里是变量的类型：

```text
Written to variable readme(str).
```

## 错误

文件不存在、路径是目录、Data Server 未启动或请求超时等情况，工具会返回文本：

```text
Tool workspace_read error: ...
```

读取非 UTF-8 的二进制文件时，用 `base64_encode = true`（得到可落盘的 Base64 文本），
或 `var_content` + `encoding = null`（得到原始 `bytes`，但不可落盘）；否则 UTF-8 解码失败
也会走上面的错误路径。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_read`。详见
[Tool Calls 索引](../../index.md)。
