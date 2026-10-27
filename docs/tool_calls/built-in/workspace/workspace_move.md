# Workspace Move

移动或重命名 Data Server 虚拟工作区中的文件或目录。只调整索引节点，文件 ID 和 payload 保持不变。

注册名：`workspace_move`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 当前虚拟路径，例如 `docs/readme.md` |
| `destination` | string | 必填 | 目标虚拟路径（包含新名称，不是目标目录），例如 `docs/archive/readme.md` |

```json
{
  "path": "docs/readme.md",
  "destination": "docs/archive/readme.md"
}
```

## 返回

移动结果，JSON 对象：

```json
{
  "source": "docs/readme.md",
  "destination": "docs/archive/readme.md"
}
```

`source` 和 `destination` 都是规范化后的虚拟路径。移动到与源相同的路径时不做任何改动，
仍返回这两个路径。

## 错误

以下情况会返回文本：

```text
Tool workspace_move error: ...
```

- `path` 为空（工作区根目录）或 `destination` 为空（服务器 403）；
- 源路径不存在（服务器 404）；
- `destination` 已存在（服务器 409）；
- `destination` 的某个已存在父级是文件（服务器 400）；
- 把目录移动到它自己的子目录下（服务器 403）；
- Data Server 无法连接或请求超时。

## 说明

- 同父目录内换名就是重命名；
- 移动目录会连同整棵子树一起移动，文件 ID 与 payload 不变；
- `destination` 的父目录不存在时会自动创建；
- 目标已存在时不会覆盖；
- 实际发生移动后会写回 `index.json` 持久化索引。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_move`。详见
[Tool Calls 索引](../../index.md)。
