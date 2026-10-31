# Workspace Truncate API

把已有工作区文件调整为指定字节数：缩短截断尾部，扩大用零字节补齐。

- **`/workspace/truncate/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **path:**
      - `path` (str): 虚拟文件路径
    - **query:**
      - `size` (int): 必填，目标字节数，必须 `>= 0`
  - **Response**
    - **type:** `JSON`
    - **Content:** 调整后的文件大小（整数）
  - **Errors**
    - `400`: `path` 为空或 `size` 为负数
    - `404`: 文件不存在
    - `400`: 目标是目录
    - `500`: Data Server 无法连接

```bash
curl -X POST "http://127.0.0.1:8000/workspace/truncate/docs/a.bin?size=1024"
# 1024
```
