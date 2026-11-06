# Sandbox Shell

按 `realspace.whitelist[path_key].shell_level` 执行受沙箱限制的 Shell 命令。

注册名：`sandbox_shell`

## 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path_key` | string | 必填 | `realspace.whitelist` 的路径 key，选择路径和 `shell_level` |
| `command` | string | 必填 | 交给系统 Shell 执行的命令 |
| `cwd` | string \| null | `null` | 工作目录；相对路径从该条目的 `path` 解析 |
| `timeout` | number \| null | `null` | 单次超时（秒）；null 使用 30 秒 |

```json
{
  "path_key": "agent",
  "command": "git status --short",
  "cwd": "project",
  "timeout": 30
}
```

## shell_level

`shell_level` 是每个路径条目自己的字段：

| 值 | 行为 |
| --- | --- |
| `off` | 禁止该路径启动 Shell |
| `read_only` | 读、执行可用；写入/删除由内核沙箱拒绝 |
| `path_write` | 只允许写 `cwd` 和私有 temp；其他路径拒绝 |
| `full_access` | 不启用沙箱，正常权限执行 |

```json
{
  "tool_calls": {
    "tools_configs": {
      "realspace": {
        "whitelist": {
          "agent": {
            "path": "./AgentWorkspace",
            "read": true,
            "write": true,
            "shell_level": "path_write"
          }
        }
      }
    }
  }
}
```

`path_key` 必须存在；`cwd` 必须是该条目 `path` 的根目录或子目录。

## 返回

```json
{
  "command": "git status --short",
  "cwd": "D:\\AgentWorkspace\\project",
  "mode": "path_write",
  "exit_code": 0,
  "stdout": "",
  "stderr": "",
  "denied": false,
  "backend": "windows-acl"
}
```

被沙箱拒绝时通常是非 0 退出码，且 `denied` 为 `true`；stderr 保留系统返回的 `Access is denied` 等信息。

## 错误

- `path_key` 不存在；
- 该条目的 `shell_level` 为 `off`；
- `cwd` 不在该条目的 `path` 下；
- 沙箱模式没有可用后端；
- 超时。

沙箱不可用时会直接返回 `SANDBOX_UNAVAILABLE`，不会降级到 `full_access`。

## 平台

- Windows：ACL restricted token；
- Linux：bwrap；
- macOS：Seatbelt；
- 其他平台：拒绝。

## 前置条件

`configs/project_configs/config.json` 中的 `tool_calls.registed` 包含 `sandbox_shell`，并且目标 `realspace.whitelist[id]` 存在。详见
[Tool Calls 索引](../../index.md)。
