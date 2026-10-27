# Workspace Get Info API

获取工作区文件的元信息。

- **`/workspace/get_info/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟文件路径
  - **Response**
    - **type:** `JSON`
    - **Content:** `FileInfo`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `size` | int | 文件大小，单位字节 |
| `st_mtime` | float | 最后修改时间（秒级时间戳） |
| `st_mtime_ns` | int | 最后修改时间（纳秒级时间戳） |
| `st_atime` | float | 最后访问时间（秒级时间戳） |
| `st_atime_ns` | int | 最后访问时间（纳秒级时间戳） |
| `st_mode` | str | `os.stat().st_mode` 的二进制字符串 |

  - **Errors**
    - `404`: 文件不存在
    - `400`: `path` 指向的是目录
    - `500`: Data Server 无法连接

```bash
curl http://127.0.0.1:8000/workspace/get_info/docs/a.md
```

```json
{
  "size": 5,
  "st_mtime": 1793081495.52,
  "st_mtime_ns": 1793081495522713100,
  "st_atime": 1793081495.54,
  "st_atime_ns": 1793081495546711800,
  "st_mode": "0b1000000110110110"
}
```
