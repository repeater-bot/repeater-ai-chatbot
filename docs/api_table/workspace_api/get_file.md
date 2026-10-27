# Workspace Get File API

读取工作区文件，返回原始字节。

- **`/workspace/get_file/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟文件路径，例如 `docs/readme.md`
  - **Response**
    - **type:** `Binary`
    - **Content-Type:** `application/octet-stream`
    - **Content:** *文件原始字节*
  - **Errors**
    - `404`: 文件不存在，或索引存在但数据文件丢失
    - `400`: `path` 指向的是目录
    - `500`: Data Server 无法连接

```bash
curl --output readme.md \
  http://127.0.0.1:8000/workspace/get_file/docs/readme.md
```

需要按文本读取时用 [Get Text](./get_text.md)，不要自行假设文件编码。
