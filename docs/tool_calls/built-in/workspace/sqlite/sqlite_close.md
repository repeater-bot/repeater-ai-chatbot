# Workspace SQLite Close

关闭 DataServer 上的 SQLite 数据库并释放访问 ID。

注册名：`workspace_sqlite_close`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `sqlite_id` | string | 必填 | 要关闭的访问 ID |

```json
{"sqlite_id": "64d6f2808edb44849c9ed34f2113b66e"}
```

返回：

```json
{
  "id": "64d6f2808edb44849c9ed34f2113b66e",
  "closed": true
}
```

ID 不存在或已关闭返回 404。

