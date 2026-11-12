# Workspace SQLite List

列出 DataServer 上所有已打开的 SQLite 数据库。

注册名：`workspace_sqlite_list`

无参数。

返回：

```json
[
  {
    "id": "40bed5400a44493c84acd5189941d471",
    "path": "D:\\data\\app.db",
    "opened_at": "2026-11-13T00:10:00.123456+00:00"
  }
]
```

按 `opened_at` 升序排列；没有打开的数据库时返回空数组。
