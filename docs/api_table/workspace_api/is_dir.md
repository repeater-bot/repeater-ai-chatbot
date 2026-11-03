# Workspace Is Dir API

判断工作区中的路径是不是目录。

- **`/workspace/is_dir/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 要判断的虚拟路径
  - **Response**
    - **type:** `JSON`
    - **Content:** `true` 或 `false`
  - **Errors**
    - `500`: Data Server 无法连接

路径不存在、路径是文件都返回 `200` 和 `false`，不会抛 404/400。

```bash
curl http://127.0.0.1:8000/workspace/is_dir/docs
# true

curl http://127.0.0.1:8000/workspace/is_dir/docs/readme.md
# false
```
