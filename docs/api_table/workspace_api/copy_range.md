# Workspace Copy Range API

把源文件的一段字节复制成新文件。

- **`/workspace/copy_range/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `JSON`
    - **path:** `path` (str)：源文件
    - **body:**
      - `destination` (str)：新文件路径
      - `start` (int)：起始偏移，`>= 0`
      - `end` (int)：结束偏移（不含），`>= start`
  - **Response**
    - **type:** `JSON`
    - **Content:** `{"source","destination","size"}`
  - **Errors**
    - `400`: 源是目录或区间非法
    - `404`: 源不存在
    - `409`: 目标已存在
    - `500`: Data Server 无法连接

```bash
curl -X POST http://127.0.0.1:8000/workspace/copy_range/docs/a.bin \
  -H "Content-Type: application/json" \
  -d '{"destination":"slices/part-1.bin","start":0,"end":1024}'
```
