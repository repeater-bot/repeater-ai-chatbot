# Workspace Get Text API

读取工作区文件并按指定编码解码为文本。

- **`/workspace/get_text/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟文件路径，例如 `docs/readme.md`
    - **query:**
      - `text_encoding` (str): 解码编码，默认 `utf-8`
  - **Response**
    - **type:** `Text`
    - **Content-Type:** `text/plain`
    - **Content:** *解码后的文件文本*
  - **Errors**
    - `404`: 文件不存在
    - `400`: `path` 指向的是目录
    - `400`: `text_encoding` 无效或内容无法按该编码解码
    - `500`: Data Server 无法连接

```bash
curl "http://127.0.0.1:8000/workspace/get_text/docs/readme.md"
curl "http://127.0.0.1:8000/workspace/get_text/docs/readme.md?text_encoding=gbk"
```

二进制文件请用 [Get File](./get_file.md)，避免解码失败。
