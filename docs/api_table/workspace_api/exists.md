# Workspace Exists API

判断工作区路径是否存在。

- **`/workspace/exists/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟路径
  - **Response**
    - **type:** `JSON`
    - **Content:** `true` 或 `false`
  - **Errors**
    - `500`: Data Server 无法连接

路径不存在不是错误，仍然返回 `200` 和 `false`。

```bash
curl http://127.0.0.1:8000/workspace/exists/docs/a.md
# true

curl http://127.0.0.1:8000/workspace/exists/docs/missing.md
# false
```

只判断存在性，不读取文件内容；也不区分文件还是目录。
