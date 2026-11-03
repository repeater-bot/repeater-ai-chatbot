# Workspace Edit API

替换工作区文件的半开字节区间 `[start, end)`。

- **`/workspace/edit/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `JSON`
    - **path:**
      - `path` (str): 虚拟文件路径
    - **body:**
      - `start` (int): 区间起始偏移，`>= 0`
      - `end` (int): 区间结束偏移（不含），`>= start`
      - `data` (str): 替换内容的 Base64 文本
  - **Response**
    - **type:** `JSON`
    - **Content:** 编辑后的文件大小（整数）
  - **Errors**
    - `400`: `path` 为空、区间非法或 Base64 非法
    - `404`: 文件不存在
    - `400`: 目标是目录
    - `500`: Data Server 无法连接

```bash
curl -X POST http://127.0.0.1:8000/workspace/edit/docs/a.bin \
  -H "Content-Type: application/json" \
  -d '{"start": 2, "end": 5, "data": "cmVwbGFjZW1lbnQ="}'
# 12
```

`start == end` 是插入，`data` 为空是删除。编辑会写新 payload，索引更新成功后才删除旧 payload。
