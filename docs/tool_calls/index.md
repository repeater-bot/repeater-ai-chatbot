# Tool Calls

让 Repeater 与程序进行交互

## Built-in Tools

1. [HTTP Requests Tool](./built-in/http_requests.md)
2. [Set Prompt Tool](./built-in/set_prompt.md)
3. [Demo Tool](./built-in/demo.md)
4. [Get Models](./built-in/get_models.md)
5. [Call Model](./built-in/call_model.md)
6. [Asteval](./built-in/asteval.md)
7. [token_count](./built-in/token_count.md)
8. [Metaso](./built-in/metaso.md)
9. [System Info](./built-in/system_info.md)
10. [Get Horizontal Ids](./built-in/horizontal_access/get_horizontal_ids.md)
11. [Horizontal Access](./built-in/horizontal_access/horizontal_access.md)
12. [Delete Horizontal Context](./built-in/horizontal_access/delete_horizontal_context.md)
13. [Starlark](./built-in/starlark.md)
14. [Generate Image](./built-in/generate_image.md)
15. [Get Dispatch Bots](./built-in/dispatch_trigger/get_dispatch_bots.md)
16. [Dispatch Trigger](./built-in/dispatch_trigger/dispatch_trigger.md)
17. [Dispatch Ask Questions](./built-in/dispatch_trigger/dispatch_ask_questions.md)
18. [Url to Image](./built-in/url_to_image.md)
19. [List Task](./built-in/list_task.md)
20. [Bypass](./built-in/bypass.md)
21. [Wait Task](./built-in/wait_task.md)
22. [Workspace Read](./built-in/workspace/workspace_read.md)
23. [Workspace Write](./built-in/workspace/workspace_write.md)
24. [Workspace Delete](./built-in/workspace/workspace_delete.md)
25. [Workspace List](./built-in/workspace/workspace_list.md)
26. [Workspace Info](./built-in/workspace/workspace_info.md)
27. [Workspace Exists](./built-in/workspace/workspace_exists.md)
28. [Workspace Glob](./built-in/workspace/workspace_glob.md)
29. [Workspace Rematch](./built-in/workspace/workspace_rematch.md)
30. [Workspace Mkdir](./built-in/workspace/workspace_mkdir.md)
31. [Workspace Move](./built-in/workspace/workspace_move.md)
32. [Workspace Copy](./built-in/workspace/workspace_copy.md)
33. [Deepseek Search](./built-in/deepseek/deepseek_search.md)
34. [Deepseek Fetch](./built-in/deepseek/deepseek_fetch.md)
35. [Variable List](./built-in/variables/variable_list.md)
36. [Variable Exists](./built-in/variables/variable_exists.md)
37. [Get Variable](./built-in/variables/get_variable.md)
38. [Set Variable](./built-in/variables/set_variable.md)
39. [Remove Variable](./built-in/variables/remove_variable.md)
40. [Load Variable](./built-in/variables/load_variable.md)
41. [Dump Variable](./built-in/variables/dump_variable.md)

> Workspace 系列工具通过 Data Server 访问虚拟工作区。使用前需要：
> 在 `configs/project_configs/config.json` 里把 `data_server.base_url` 指向运行中的
> Data Server，并把工具名加入 `tool_calls.registed`；用户侧还要在
> `allowed_tool_calls`（或 `tool_calls.allowed_by_default`）中允许，模型才能调用。

> Variables 系列工具维护每个用户自己的变量表，按 `user_id` 隔离。变量只存在进程内存里，
> 必须显式调用 `dump_variable` 才写入 `ProgramData.variables`，重启后用 `load_variable`
> 读回；值为 `bytes` 的变量会让 `dump_variable` 整份失败，用 `variable_list` 的类型列定位。
> 这 7 个注册名**默认不开启**：需要在目标环境的 `configs/project_configs/config.json` 里
> 把工具名加入 `tool_calls.registed`，并在 `allowed_tool_calls`（或
> `tool_calls.allowed_by_default`）中允许。开发环境和用户环境各有一份自己的配置，
> 不要假定某一份里已经加好。