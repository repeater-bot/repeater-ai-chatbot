# Variable Exists

判断某个变量名是否存在于当前用户的变量表中，用于写入前查重。

注册名：`variable_exists`（类名 `VariableExists`，实现见 `core/tool_caller/tools/variables/variable_exists.py`）

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `variable_name` | string | 必填 | 要检查的变量名 |

```json
{
  "variable_name": "reply"
}
```

## 返回

文本形式的布尔结论，注意原文是英文：

```text
Variable 'reply' already exists.
```

```text
Variable 'reply' does not exist.
```

## 说明

- 判断的是**键是否存在**，与值的真假无关。值为 `null`（或任何被判定为假的值）时也算存在，
  且 [`get_variable`](./get_variable.md) 能把它读成 `null`，两个工具口径一致。
- 用户没有任何变量时直接返回 `does not exist`，不会报错。

## 前置条件

本工具**默认不开启**。启用时需要在目标环境的 `configs/project_configs/config.json` 里，
把 `variable_exists` 加入 `tool_calls.registed`，并在 `allowed_tool_calls`
（或 `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
以目标环境的实际配置为准。详见 [Tool Calls 索引](../index.md)。
