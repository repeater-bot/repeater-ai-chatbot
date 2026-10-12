# Wait Task

等待由 `bypass` 启动的任务结束，并返回它的结果

注册名：`wait_task`

接受一个参数
``` json
{
  "task_id": "3f8a1c2e-4b5d-4e6f-8a9b-0c1d2e3f4a5b" // The id of the task to wait for.
}
```

返回该任务的输出内容（等同于直接调用该工具时模型收到的内容）

任务不存在时返回 `No task with id ...`
