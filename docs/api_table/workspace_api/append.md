# Workspace Append API

向工作区文件追加原始字节；文件不存在时自动创建，并补齐中间目录。

- **`/workspace/append/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `application/octet-stream`
    - **path:**
      - `path` (str): 目标文件虚拟路径
    - **body:** 要追加的原始字节
  - **Response**
    - **type:** `JSON`
    - **Content:** 追加后的文件大小（整数）
  - **Errors**
    - `400`: `path` 为空
    - `400`: 目标是目录
    - `400`: 父路径是文件
    - `500`: Data Server 无法连接

```bash
printf 'tail' | curl --data-binary @- \
  -H "Content-Type: application/octet-stream" \
  http://127.0.0.1:8000/workspace/append/docs/a.bin
```
