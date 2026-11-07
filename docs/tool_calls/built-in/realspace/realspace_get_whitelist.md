# Realspace Get Whitelist

返回当前 realspace 白名单条目，以及每个条目允许的操作。

注册名：`realspace_get_whitelist`

## 参数

无参数。

```json
{}
```

## 返回

白名单条目字典。每个条目包含 `path`、`read`、`write`、`shell_level`：

```json
{
  "agent": {
    "path": "D:\\Allowed",
    "read": true,
    "write": false,
    "shell_level": "off"
  }
}
```

## 错误

正常情况不会因路径失败；配置未加载或模型校验失败时返回工具错误文本。

## 白名单

`realspace_get_whitelist` 不需要自己的白名单字段；它返回以键为索引的白名单字典。

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": {
          "agent": {
            "path": "D:\\Allowed",
            "read": true,
            "write": false
          }
        }
      }
    }
  }
}
```

## 前置条件


`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `realspace_get_whitelist`。详见
[Tool Calls 索引](../../index.md)。
