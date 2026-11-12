# Workspace SQLite Execute

使用访问 ID 在 DataServer 上执行一条 SQL。

注册名：`workspace_sqlite_execute`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `sqlite_id` | string | 必填 | `workspace_sqlite_create` / `workspace_sqlite_open` 返回的 ID |
| `sql` | string | 必填 | 单条 SQL |
| `params` | array \| object \| null | `null` | 位置参数或命名参数 |

```json
{
  "sqlite_id": "64d6f2808edb44849c9ed34f2113b66e",
  "sql": "INSERT INTO items (name) VALUES (?)",
  "params": ["alpha"]
}
```

返回 `columns`、`rows`、`rowcount`、`lastrowid`；BLOB 以 `{"$base64": "..."}` 返回。
