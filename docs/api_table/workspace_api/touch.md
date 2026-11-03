# Workspace Touch API

创建空文件，或刷新已有文件的修改时间。

- **`/workspace/touch/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **path:**
      - `path` (str): 虚拟文件路径
  - **Response**
    - **type:** `JSON`
    - **Content:** 当前文件大小（整数；新建时为 0）
  - **Errors**
    - `400`: `path` 为空
    - `400`: 目标是目录
    - `400`: 父路径是文件
    - `500`: Data Server 无法连接

```bash
curl -X POST http://127.0.0.1:8000/workspace/touch/docs/new.bin
# 0
```

已存在的文件不会被清空，只刷新 mtime。
