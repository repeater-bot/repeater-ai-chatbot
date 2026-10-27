# Workspace Glob API

在指定目录下按 glob 模式匹配虚拟路径。

- **`/workspace/glob/{path:path}`**
  - **Request**
    - **method:** `GET`
    - **path:**
      - `path` (str): 扫描起始目录；根目录用 `/workspace/glob/`
    - **query:**
      - `pattern` (str): 必填，glob 模式
      - `recursive` (bool): 默认 `false`；`true` 时等价于 `**/<pattern>`
  - **Response**
    - **type:** `JSON`
    - **Content:** *完整虚拟路径数组，可能包含目录*
  - **Errors**
    - `404`: 起始目录不存在
    - `400`: 起始路径是文件
    - `400`: `pattern` 为空
    - `422`: 缺少 `pattern`
    - `500`: Data Server 无法连接

匹配规则：

- `*` / `?` / `[...]` 只匹配一个路径段；
- `**` 可以跨任意层目录；
- 裸模式（不含 `/` 和 `**`）只匹配直接子项；
- `recursive=true` 时在起始目录下按任意深度匹配。

```bash
curl "http://127.0.0.1:8000/workspace/glob/docs?pattern=*.md"
# ["docs/a.md"]

curl "http://127.0.0.1:8000/workspace/glob/docs?pattern=*.md&recursive=true"
# ["docs/a.md", "docs/sub/c.md"]
```

只匹配单条路径请用 [Rematch](./rematch.md)；需要全部后代路径不带模式时用
[List Dir](./list_dir.md) 的 `recursive=true`。
