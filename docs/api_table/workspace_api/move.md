# Workspace Move API

移动或重命名工作区中的文件或目录；只调整索引节点，文件 ID 和 payload 保持不变。

- **`/workspace/move/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `JSON`
    - **path:**
      - `path` (str): 源虚拟路径，例如 `docs/readme.md`
    - **body:**
      - `destination` (str): 目标虚拟路径，需要写出新名称，例如 `docs/archive/readme.md`
  - **Response**
    - **type:** `JSON`
    - **Content:** `MoveResult`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `source` | str | 规范化后的源路径，即移动前的位置 |
| `destination` | str | 规范化后的目标路径 |

  - **Errors**
    - `404`: 源路径不存在
    - `409`: `destination` 已存在
    - `403`: 源路径为根目录，或 `destination` 为空
    - `403`: 把目录移动到它自己的子目录下
    - `400`: `destination` 的某个已存在父级是文件
    - `422`: 缺少 `destination` 字段
    - `500`: Data Server 无法连接

移动文件：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"destination": "docs/archive/readme.md"}' \
  http://127.0.0.1:8000/workspace/move/docs/readme.md
```

```json
{
  "source": "docs/readme.md",
  "destination": "docs/archive/readme.md"
}
```

同父目录内换名就是重命名：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"destination": "docs/README.md"}' \
  http://127.0.0.1:8000/workspace/move/docs/readme.md
```

- `destination` 是移动后的完整路径（含新名称），不是目标目录；
- 只改索引，文件 ID 与 payload 都不变，不会复制数据；移动目录会连同整棵子树一起移动；
- 源与目标相同时是 no-op，不产生任何改动，仍返回 `200` 和这两个路径；
- `destination` 的父目录不存在时会自动创建；目标已存在时不会覆盖。
