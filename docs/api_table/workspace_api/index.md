# Workspace API

通过 Backend 的 `DataClient` 访问工作区，不需要直接连接 Data Server。

所有 `path` 都是相对工作区根目录的虚拟路径，**不带开头的 `/`**；
接口本身不额外鉴权，鉴权/访问控制应放在反向代理或上层。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | [`/workspace/get_file/{path:path}`](./get_file.md) | 读取文件原始字节 |
| `GET` | [`/workspace/get_text/{path:path}`](./get_text.md) | 按文本读取文件 |
| `GET` | [`/workspace/list_dir/{path:path}`](./list_dir.md) | 列出直接子项或递归后代 |
| `GET` | [`/workspace/glob/{path:path}`](./glob.md) | glob 模式匹配 |
| `GET` | [`/workspace/rematch/{path:path}`](./rematch.md) | 正则匹配单条路径 |
| `GET` | [`/workspace/get_info/{path:path}`](./get_info.md) | 文件元信息 |
| `GET` | [`/workspace/exists/{path:path}`](./exists.md) | 判断路径是否存在 |
| `GET` | [`/workspace/is_file/{path:path}`](./is_file.md) | 判断路径是否为文件 |
| `GET` | [`/workspace/is_dir/{path:path}`](./is_dir.md) | 判断路径是否为目录 |
| `POST` | [`/workspace/write_file/{path:path}`](./write_file.md) | 写入文件 |
| `POST` | [`/workspace/append/{path:path}`](./append.md) | 追加原始字节 |
| `POST` | [`/workspace/truncate/{path:path}`](./truncate.md) | 调整文件大小 |
| `POST` | [`/workspace/touch/{path:path}`](./touch.md) | 创建空文件或刷新 mtime |
| `POST` | [`/workspace/edit/{path:path}`](./edit.md) | 替换字节区间（Base64） |
| `POST` | [`/workspace/mkdir/{path:path}`](./mkdir.md) | 创建目录，自动补齐中间目录 |
| `POST` | [`/workspace/move/{path:path}`](./move.md) | 移动或重命名，body 为 `{"destination": "..."}` |
| `POST` | [`/workspace/copy/{path:path}`](./copy.md) | 复制文件或目录树，body 为 `{"destination": "..."}` |
| `DELETE` | [`/workspace/delete/{path:path}`](./delete.md) | 删除文件或目录 |
| `GET` | [`/workspace/hash/{path:path}`](./hash.md) | 计算 SHA-256 |
| `GET` | [`/workspace/du/{path:path}`](./du.md) | 统计字节数/文件数/目录数 |
| `GET` | [`/workspace/tree/{path:path}`](./tree.md) | 返回嵌套树 |
| `POST` | [`/workspace/copy_range/{path:path}`](./copy_range.md) | 把字节区间复制成新文件 |

这些端点与 `DataClient` 的公开操作一一对应：

```text
get_file / get_text / list_dir / glob / rematch
get_info / exists / is_file / is_dir / write_file
append / truncate / touch / edit
mkdir / move / copy / copy_range / delete
hash / du / tree
```

`DataClient.close()`、`base_url`、`quote_path()`、`operation_url()` 属于生命周期或内部工具，
没有对应的 HTTP 端点。
