# Variable List

列出当前用户在内存变量表中的全部变量名，以及每个值的类型。

注册名：`variable_list`（类名 `VariablesList`，实现见 `core/tool_caller/tools/variables/variables_list.py`）

## 参数

一个参数，用于筛选变量名：

```json
{
  "pattern": "^[\\s\\S]*$" // The pattern to match variable names.
}
```

## 返回

对象数组，按插入顺序返回，`type` 是该值的 Python 类型名：

```json
{
  "readme": "str",
  "blob": "bytes"
}
```

没有变量时返回空数组 `[]`。类型名取自 `type(value).__name__`，所以会出现
`str`、`bytes`、`dict`、`list`、`int`、`bool`、`NoneType` 等。

## 为什么要看类型

`dump_variable` 遇到 `bytes` 变量会整份失败，只返回 `Variables cannot be dumped.`，
不说是哪个变量。用本工具过滤 `type = "bytes"` 就能定位到具体变量——这类变量通常来自
`set_variable` 带了 `encoding`，或 `workspace_read` 的 `var_content` 没给 `encoding`。
详见 [Dump Variable](./dump_variable.md)。

## 说明

- 只列出**内存中**的变量，是否已 `dump_variable` 持久化不影响结果。
- 变量按 `runtime.user_id` 隔离，不存在跨用户可见的变量。
- 只返回名字和类型，不返回值；读值请用 `get_variable`。
- 读取过程持有 `ToolsCaller.variable_lock`，结果是加锁期间的一致快照。

## 前置条件

本工具**默认不开启**。启用时需要在目标环境的 `configs/project_configs/config.json` 里，
把 `variable_list` 加入 `tool_calls.registed`，并在 `allowed_tool_calls`
（或 `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
以目标环境的实际配置为准。详见 [Tool Calls 索引](../../index.md)。
