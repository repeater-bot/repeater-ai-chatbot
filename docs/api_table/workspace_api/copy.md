# Workspace Copy API

复制文件或目录；目录会被递归克隆，每个文件都分配新的文件 ID 并复制一份 payload，源保持不变。

- **`/workspace/copy/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `JSON`
    - **path:**
      - `path` (str): 源虚拟路径，例如 `docs`
    - **body:**
      - `destination` (str): 目标虚拟路径，需要写出新名称，例如 `backup/docs`
  - **Response**
    - **type:** `JSON`
    - **Content:** `CopyResult`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `source` | str | 规范化后的源路径 |
| `destination` | str | 规范化后的目标路径 |
| `copied_files` | int | 复制出的文件数 |
| `copied_dirs` | int | 复制出的目录数，包含被复制的根目录本身；复制单个文件时为 `0` |

  - **Errors**
    - `404`: 源路径不存在
    - `409`: `destination` 已存在，包括 `destination` 与源路径相同
    - `403`: 源路径为根目录，或 `destination` 为空
    - `403`: 把目录复制到它自己的子目录下
    - `400`: `destination` 的某个已存在父级是文件
    - `422`: 缺少 `destination` 字段
    - `500`: Data Server 无法连接

复制单个文件：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"destination": "docs/a.copy.md"}' \
  http://127.0.0.1:8000/workspace/copy/docs/a.md
```

```json
{
  "source": "docs/a.md",
  "destination": "docs/a.copy.md",
  "copied_files": 1,
  "copied_dirs": 0
}
```

递归复制目录：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"destination": "backup/docs"}' \
  http://127.0.0.1:8000/workspace/copy/docs
```

```json
{
  "source": "docs",
  "destination": "backup/docs",
  "copied_files": 3,
  "copied_dirs": 2
}
```

- `destination` 是复制后的完整路径（含新名称），不是目标目录；
- `copied_dirs` 包含被复制的根目录本身：`docs` 下有 1 个子目录时，复制 `docs` 的
  `copied_dirs` 是 `2`（根目录 + 子目录）；复制单个文件时为 `0`；
- 每个文件都会拿到新的文件 ID，payload 是独立副本，之后修改副本不影响源；
- 源路径保持不变，只有目标侧出现新节点；
- `destination` 的父目录不存在时会自动创建；目标已存在时不会覆盖，也不会与已有目录合并。
