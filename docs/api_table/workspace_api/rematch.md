# Workspace Rematch API

用 Python 正则表达式匹配单条虚拟路径。

- **`/workspace/rematch/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 要匹配的虚拟路径
    - **query:**
      - `pattern` (str): 必填，Python 正则表达式
  - **Response**
    - **type:** `JSON`
    - **Content:** `true` 或 `false`
  - **Errors**
    - `400`: `pattern` 为空
    - `400`: 正则表达式非法
    - `422`: 缺少 `pattern`
    - `500`: Data Server 无法连接

使用 `re.match`，从路径开头匹配；**不检查路径是否真实存在**。

```bash
curl "http://127.0.0.1:8000/workspace/rematch/docs/a.md?pattern=.*\.md$"
# true

curl "http://127.0.0.1:8000/workspace/rematch/docs/a.md?pattern=\.md$"
# false（re.match 从开头匹配）
```

要判断存在性用 [Exists](./exists.md)；要扫描目录用 [Glob](./glob.md)。
