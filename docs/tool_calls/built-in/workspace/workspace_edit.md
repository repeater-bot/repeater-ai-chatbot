# Workspace Edit

替换 Data Server 虚拟工作区文件的字节区间。

注册名：`workspace_edit`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | string | 必填 | 虚拟文件路径 |
| `data` | string | 必填 | 替换内容的 Base64 文本 |
| `start` | integer | 必填 | 区间起始偏移，`>= 0` |
| `end` | integer | 必填 | 区间结束偏移（不含），`>= start` |

```json
{
  "path": "docs/a.bin",
  "start": 2,
  "end": 5,
  "data": "cmVwbGFjZW1lbnQ="
}
```

## 返回

编辑后的文件大小，作为十进制文本返回：

```text
12
```

## 说明

- 区间是 `[start, end)`；
- `start == end` 表示插入；
- `data` 为空表示删除该区间；
- 编辑会分配新 payload ID，索引更新成功后才删除旧 payload。

## 错误

以下情况会返回文本：

```text
Tool workspace_edit error: ...
```

- 文件不存在（404）；
- 目标是目录（400）；
- 区间非法或越界（400）；
- Base64 非法（400）；
- Data Server 无法连接或请求超时。

## 前置条件

`configs/project_configs/config.json` 中的 `data_server.base_url` 指向运行中的 Data Server，
并且 `tool_calls.registed` 包含 `workspace_edit`。详见
[Tool Calls 索引](../../index.md)。
