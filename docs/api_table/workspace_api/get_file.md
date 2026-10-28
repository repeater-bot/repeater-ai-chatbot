# Workspace Get File API

读取工作区文件，返回原始字节。

- **`/workspace/get_file/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 虚拟文件路径，例如 `docs/readme.md`
    - **headers:**
      - `Range` (str): 可选，标准字节区间，例如 `bytes=0-1023`、`bytes=1024-`、`bytes=-512`
      - `If-Range` (str): 可选，原样透传给 Data Server
  - **Response**
    - **type:** `Binary`
    - **Content-Type:** `application/octet-stream`
    - **Content:** *完整文件字节（200）或区间字节（206）*
    - **Headers:** `Accept-Ranges: bytes`；206 时带 `Content-Range: bytes <start>-<end>/<size>`
  - **Errors**
    - `416`: `Range` 非法或越界
    - `404`: 文件不存在，或索引存在但数据文件丢失
    - `400`: `path` 指向的是目录
    - `500`: Data Server 无法连接

```bash
# 完整读取
curl --output readme.md \
  http://127.0.0.1:8000/workspace/get_file/docs/readme.md

# 按字节区间读取
curl -H "Range: bytes=0-1023" \
  --output first-1k.bin \
  http://127.0.0.1:8000/workspace/get_file/docs/readme.md
```

`Range` 通过请求头透传给 Data Server；206 和 `Content-Range` 会原样返回给调用方。
需要按文本读取时用 [Get Text](./get_text.md)，不要自行假设文件编码。
