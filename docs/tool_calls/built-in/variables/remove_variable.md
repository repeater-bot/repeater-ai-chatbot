# Remove Variable

从当前用户的变量表中删除一个变量。

注册名：`remove_variable`（类名 `RemoveVariable`，实现见 `core/tool_caller/tools/variables/remove_variable.py`）

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `variable_name` | string | 必填 | 要删除的变量名 |

```json
{
  "variable_name": "reply"
}
```

## 返回

```text
Variable removed.
```

## 说明

- 幂等：变量不存在时不报错，同样返回 `Variable removed.`，只是没有任何变化。
- 删除后该用户的变量表为空时，内存中对应的用户条目会一并清掉。
- 只改**内存**，已落盘的副本要靠 `dump_variable` 才会同步；只删内存不 dump 的话，
  下次 `load_variable` 会把旧值重新载回来。
- 删除过程持有 `ToolsCaller.variable_lock`。

## 前置条件

`configs/project_configs/config.json` 的 `tool_calls.registed` 必须包含 `remove_variable`，
用户侧还要在 `allowed_tool_calls`（或 `tool_calls.allowed_by_default`）中允许。详见
[Tool Calls 索引](../index.md)。
