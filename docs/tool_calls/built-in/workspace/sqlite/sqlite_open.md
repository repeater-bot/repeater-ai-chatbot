# Workspace SQLite Open

打开 DataServer 上的已有 SQLite 数据库，并返回访问 ID。

注册名：`workspace_sqlite_open`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 已有数据库文件路径 |

```json
{"path": "databases/app.db"}
```

返回：

```json
{
  "id": "64d6f2808edb44849c9ed34f2113b66e",
  "path": "databases/app.db"
}
```

文件不存在返回 404；不是 SQLite 返回 400。

