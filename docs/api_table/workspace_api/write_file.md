# Workspace Write File API

把上传的文件写入工作区。

- **`/workspace/write_file/{path:path}`**
  - **Request**
    - **method:** `POST`
    - **type:** `multipart/form-data`
    - **path:**
      - `path` (str): 目标虚拟文件路径
    - **form:**
      - `file` (file): 必填，文件内容；文件名和 Content-Type 会传给 `DataClient.write_file`
  - **Response**
    - **type:** `JSON`
    - **Content:** *写入的字节数（整数）*
  - **Errors**
    - `400`: 目标路径为空
    - `400`: 目标路径是目录
    - `400`: 父路径是文件
    - `422`: 缺少 `file` 字段
    - `500`: Data Server 无法连接

目标不存在时会自动创建文件节点和中间目录；同名文件会被覆盖。

```bash
curl -F "file=@readme.md" \
  http://127.0.0.1:8000/workspace/write_file/docs/readme.md
# 1234
```

不需要先创建目录；`/workspace/write_file/a/b/c.txt` 会自动创建 `a/b`。
