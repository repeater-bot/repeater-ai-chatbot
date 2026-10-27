# Dump Variable

把当前用户内存变量表整体序列化，写进该用户的持久化程序数据。

注册名：`dump_variable`（类名 `DumpVariables`，实现见 `core/tool_caller/tools/variables/dump_vars.py`；
注意类名是复数 `Variables`，注册名是单数 `dump_variable`）

## 参数

无参数，调用时传空对象：

```json
{}
```

## 返回

```text
Variable dumped.
```

序列化失败时：

```text
Variables cannot be dumped.
```

## 写入位置

`ProgramDataManager.load(user_id)` → 覆盖 `ProgramData.variables` → `save(user_id)`。
只改 `variables` 一个字段，`ProgramData` 的其他字段先读后写，保持原值。

## 行为细节

- 内存里没有该用户的变量表时，按空字典处理，落盘结果是 `"{}"`，同样返回 `Variable dumped.`。
- 序列化用 `orjson.dumps`，所以**变量值必须 JSON 可序列化**。通过 `set_variable` 指定
  `encoding` 存进去的 `bytes` 无法序列化，此时整份变量都会 dump 失败并返回
  `Variables cannot be dumped.`——是整份失败，不是跳过那一个变量，一个坏值会卡住全部落盘。
- 失败时**不会写盘**，`ProgramData.variables` 保持上一次成功落盘的内容。
- 序列化在锁内完成，之后才访问 `ProgramDataManager`，锁不会跨越磁盘 I/O。
- 落盘是**替换**语义：内存删除过的变量会从持久化数据里一并消失。

## 排错：找出导致失败的变量

失败信息不说是哪个变量，但 [`variable_list`](./variable_list.md) 会返回每个变量的类型。
过滤 `type = "bytes"` 即可定位：

- 来自 `set_variable` 带了 `encoding`；
- 来自 `workspace_read` 的 `var_content` 没给 `encoding`（此时变量存的是原始 `bytes`）。

删除或用 `set_variable` 不带 `encoding` 重写该变量后再 dump。

## 常见问题

| 现象 | 原因 |
| --- | --- |
| `Variables cannot be dumped.` | 变量里存在 `bytes`（`set_variable` 带了 `encoding`）或其他非 JSON 类型；用 `variable_list` 看类型 |
| 重启后变量没了 | 只调了 `set_variable` 没调 `dump_variable` |
| `load_variable` 返回 `Invalid variables string.` | 持久化内容不是合法 JSON，通常是外部写坏了 `ProgramData.variables` |

## 前置条件

本工具**默认不开启**。启用时需要在目标环境的 `configs/project_configs/config.json` 里，
把 `dump_variable` 加入 `tool_calls.registed`，并在 `allowed_tool_calls`
（或 `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
以目标环境的实际配置为准。详见 [Tool Calls 索引](../../index.md)。
