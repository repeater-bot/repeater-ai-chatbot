# Workspace Mkdir API

创建目录；缺失的中间目录会自动补齐。

- **`/workspace/mkdir/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **path:**
      - `path` (str): 目标虚拟目录路径，例如 `docs/notes`
    - **body:** 无
  - **Response**
    - **type:** `JSON`
    - **Content:** *规范化后的目录路径（单个 JSON 字符串，不是对象）*
  - **Errors**
    - `409`: 目标路径已存在，文件或目录都算
    - `400`: 中间路径是文件
    - `403`: `path` 为空或为根目录
    - `500`: Data Server 无法连接

```bash
curl -X POST http://127.0.0.1:8000/workspace/mkdir/docs/notes
# "docs/notes"
```

返回值是规范化后的路径；规范化会去掉首尾的 `/` 和空路径段，
所以请求 `docs//notes/` 同样返回 `"docs/notes"`。

不需要逐级创建：`/workspace/mkdir/a/b/c` 会同时补出 `a` 和 `a/b`。
目标已存在时不会覆盖，也不会静默成功，而是返回 `409`。
