# Load Variable

把当前用户已持久化的变量读回内存变量表。

注册名：`load_variable`（类名 `LoadVariables`，实现见 `core/tool_caller/tools/variables/load_vars.py`；
注意类名是复数 `Variables`，注册名是单数 `load_variable`）

## 参数

无参数，调用时传空对象：

```json
{}
```

## 返回

```text
Variable loaded.
```

失败时：

```text
Invalid variables string.
```

```text
Variables must be a JSON object.
```

## 数据来源

读取 `ProgramDataManager.load(user_id)` 返回的 `ProgramData.variables` 字段——一个由
[`dump_variable`](./dump_variable.md) 写入的 JSON 字符串。该字段默认值是空字符串 `""`：
空串按**空变量表**处理，返回 `Variable loaded.` 并把内存表置为 `{}`，所以从未 dump 过的
用户调用本工具是正常的，不是配置错误。

## 失败口径

| 情况 | 返回 |
| --- | --- |
| `ProgramData.variables` 是空串 `""` / `None` | `Variable loaded.`，内存表置空 |
| 不是合法 JSON | `Invalid variables string.` |
| 是合法 JSON 但不是对象（如 `"null"`、`"[1,2]"`、`"3"`） | `Variables must be a JSON object.` |

第三种情况必须拒绝：把非 `dict` 写进 `ToolsCaller.variables[user_id]` 之后，
`set_variable` 会直接抛 `TypeError`，该用户后续所有变量操作都会坏掉。

## 行为细节

- 解析成功后**整体替换**该用户的内存变量表，不是逐键合并；原来的内存变量会被丢弃。
- 解析失败时内存变量表保持原样，不会变成空表，也不会被清空。
- 解析在拿锁之前完成，写回内存时持有 `ToolsCaller.variable_lock`。
- 读写的是 `branch_id = None` 的主分支程序数据，与其他 `ProgramData` 字段无冲突。

## 典型生命周期

1. `set_variable` 写内存；
2. `dump_variable` 把内存变量序列化进 `ProgramData.variables` 并保存；
3. 进程重启后调用 `load_variable` 把数据读回内存。

进程刚启动时内存变量表是空的，本工具不会自动执行。

## 前置条件

本工具**默认不开启**。启用时需要在目标环境的 `configs/project_configs/config.json` 里，
把 `load_variable` 加入 `tool_calls.registed`，并在 `allowed_tool_calls`
（或 `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
以目标环境的实际配置为准。详见 [Tool Calls 索引](../../index.md)。
