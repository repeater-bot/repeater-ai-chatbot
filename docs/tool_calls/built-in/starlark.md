# Starlark

Repeater 的 Starlark 适配器
允许 AI 在 Repeater 中运行 Starlark 脚本

注册名：`starlark`

接受一个参数
``` json
{

  "source": "", // The starlark code source
  "root_stack_frame_name": "<repeater_starlark_interpreter>", // The name of the root stack frame.
  "predeclared": null, // The variables to declare before evaluating the expression.
  "universal": null, // The variables to declare before evaluating the expression.
  "max_steps": null, // The maximum number of steps to execute. (Default: None)
  "max_allocs": null, // The maximum number of allocations to execute. (Default: None)
  "timeout": 5 // The timeout for the evaluation.
}
```


返回执行结果
``` json
{
  "result": 42, // The result of the executed expression.
  "error": "", // The error message if the expression execution fails.
  "traceback": "" // The traceback if the expression execution fails.
}
```
PS: 通常来说，`error` 指的是无执行栈错误，`traceback` 则是有执行栈错误，二者互斥。