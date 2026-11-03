# Workspace Tree API

返回工作区路径的嵌套树。

- **`/workspace/tree/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:** `path` (str)，根目录传空字符串
    - **query:** `max_depth` (int)，默认 `-1`；`0` 只返回根节点
  - **Response**
    - **type:** `JSON`
    - **Content:** 文件 `{"path","type":"file","size"}`；目录 `{"path","type":"directory","children":[...]}`
  - **Errors**
    - `400`: `max_depth < -1`
    - `404`: 路径不存在
    - `500`: Data Server 无法连接

```bash
curl "http://127.0.0.1:8000/workspace/tree/docs?max_depth=2"
```
