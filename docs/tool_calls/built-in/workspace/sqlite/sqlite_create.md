# Workspace SQLite Create

在 DataServer 上新建 SQLite 数据库，并返回访问 ID。

注册名：`workspace_sqlite_create`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 新数据库文件路径 |

```json
{"path": "D:\\data\\app.db"}
```

返回：

```json
{
  "id": "64d6f2808edb44849c9ed34f2113b66e",
  "path": "D:\\data\\app.db"
}
```

文件已存在返回 409；父目录不存在返回 400。
