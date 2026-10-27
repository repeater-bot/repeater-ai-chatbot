# Workspace Mkdir

在 Data Server 的虚拟工作区中创建目录；缺失的中间目录会被一并创建。

注册名：`workspace_mkdir`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 要创建的虚拟目录路径，例如 `docs/notes` |

```json
{
  "path": "docs/notes"
}
```

## 返回

创建成功时返回规范化后的虚拟路径字符串，作为文本返回：

```text
docs/notes
```

规范化会去掉首尾的 `/` 和空路径段，所以传入 `"/docs//notes/"` 同样返回 `docs/notes`。

## 错误

以下情况会返回文本：

```text
Tool workspace_mkdir error: ...
```

- `path` 为空或只包含 `/`（客户端直接拒绝）；
- 目标路径已存在，无论它是文件还是目录（服务器 409）；
- 路径中某个已存在的父级是文件（服务器 400）；
- Data Server 无法连接或请求超时。

## 说明

- 缺失的中间目录会自动创建，不需要逐级调用；
- 目标已存在时不会覆盖，也不会返回成功，而是走上面的错误路径；
- 新建的目录节点会写回 `index.json`，重启服务后仍可读取。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_mkdir`。详见
[Tool Calls 索引](../../index.md)。
