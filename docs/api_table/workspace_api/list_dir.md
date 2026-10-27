# Workspace List Dir API

列出工作区目录的直接子项，或递归列出全部后代路径。

- **`/workspace/list_dir/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟目录路径；根目录用 `/workspace/list_dir/`
    - **query:**
      - `recursive` (bool): 默认 `false`；`true` 时递归列出所有后代
  - **Response**
    - **type:** `JSON`
    - **Content:** *完整虚拟路径数组，文件和目录都包含*
  - **Errors**
    - `404`: 目录不存在
    - `400`: `path` 指向的是文件
    - `500`: Data Server 无法连接

根目录直接子项：

```bash
curl http://127.0.0.1:8000/workspace/list_dir/
# ["docs", "images"]
```

递归：

```bash
curl "http://127.0.0.1:8000/workspace/list_dir/docs?recursive=true"
# ["docs/a.md", "docs/sub", "docs/sub/c.md"]
```

`recursive=false` 只返回直接子项；`recursive=true` 返回所有后代，**不含起始目录自身**。
