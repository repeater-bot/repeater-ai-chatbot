# Realspace Get Whitelist

返回当前 realspace 白名单条目，以及每个条目允许的操作。

注册名：`realspace_get_whitelist`

## 参数

无参数。

```json
{}
```

## 返回

白名单条目列表。每个条目包含 `path` 和全部操作 bool，例如：

```json
[
  {
    "path": "D:\\Allowed",
    "read": true,
    "read_text": true,
    "write": false,
    "copy": false
  }
]
```

`copy` 在 Python 模型里是 `copy_`，这里按配置名输出。

## 错误

正常情况不会因路径失败；配置未加载或模型校验失败时返回工具错误文本。

## 白名单

`realspace_get_whitelist` 本身不需要白名单字段，它用于让 AI 先确认当前有哪些路径、每个操作是否开放。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": [
          {
            "path": "D:\\Allowed",
            "read": true
          }
        ]
      }
    }
  }
}
```

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_get_whitelist`。详见
[Tool Calls 索引](../../index.md)。
