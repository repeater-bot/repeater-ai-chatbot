# Workspace Hash API

计算工作区文件的 SHA-256 摘要。

- **`/workspace/hash/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:** `path` (str)
    - **query:** `algorithm` (str)，默认 `sha256`，目前只支持 SHA-256
  - **Response**
    - **type:** `JSON`
    - **Content:** `{"algorithm","digest","size"}`
  - **Errors**
    - `400`: 不支持的算法
    - `404`: 文件不存在
    - `400`: 路径是目录
    - `500`: Data Server 无法连接

```bash
curl http://127.0.0.1:8000/workspace/hash/docs/a.bin
```
