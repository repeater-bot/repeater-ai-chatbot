# Bypass

在后台运行一个工具，不等待它结束，直接拿到它的任务 ID

注册名：`bypass`

接受三个参数
``` json
{
  "tool_name": "system_info", // The name of the tool to run
  "args": "", // The arguments to pass to the tool, as a JSON string.
  "timeout": null // The timeout in seconds for the tool to complete. If not specified, the tool will run indefinitely.
}
```

返回该任务的任务 ID：
``` python
"3f8a1c2e-4b5d-4e6f-8a9b-0c1d2e3f4a5b"
```

**注意：** 任务在后台运行，结果需要用 `wait_task` 获取，还在跑的任务可以用 `list_task` 查看。
