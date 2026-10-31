# Workspace Du API

统计工作区文件或目录树的总字节数、文件数和目录数。

- **`/workspace/du/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:** `path` (str)，根目录传空字符串
  - **Response**
    - **type:** `JSON`
    - **Content:** `{"path","size","files","dirs"}`
  - **Errors**
    - `404`: 路径不存在
    - `500`: Data Server 无法连接

`dirs` 包含目标目录自身；文件返回 `files=1, dirs=0`。

```bash
curl http://127.0.0.1:8000/workspace/du/docs
```
