# Workspace Delete API

删除工作区文件或目录。

- **`/workspace/delete/{path:path}`**
  - **Request**
    - **method:** `DELETE`
    - **path:**
      - `path` (str): 要删除的虚拟路径
    - **query:**
      - `recursive` (bool): 默认 `false`；删除非空目录时必须为 `true`
  - **Response**
    - **type:** `JSON`
    - **Content:** `DeleteResult`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `deleted_files` | int | 删除的文件数 |
| `deleted_dirs` | int | 删除的目录数，包含目标目录本身 |

  - **Errors**
    - `404`: 路径不存在
    - `409`: 目录非空且 `recursive=false`
    - `403`: 尝试删除根目录
    - `500`: Data Server 无法连接

删除文件：

```bash
curl -X DELETE http://127.0.0.1:8000/workspace/delete/docs/readme.md
# {"deleted_files": 1, "deleted_dirs": 0}
```

递归删除目录：

```bash
curl -X DELETE "http://127.0.0.1:8000/workspace/delete/docs?recursive=true"
# {"deleted_files": 3, "deleted_dirs": 2}
```

`recursive=false` 只能删文件或空目录；非空目录会返回 `409`。
