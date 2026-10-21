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
10. [Get Horizontal Ids](./built-in/get_horizontal_ids.md)
11. [Horizontal Access](./built-in/horizontal_access.md)
12. [Delete Horizontal Context](./built-in/delete_horizontal_context.md)
13. [Starlark](./built-in/starlark.md)
14. [Generate Image](./built-in/generate_image.md)
15. [Get Dispatch Bots](./built-in/get_dispatch_bots.md)
16. [Dispatch Trigger](./built-in/dispatch_trigger.md)
17. [Dispatch Ask Questions](./built-in/dispatch_ask_questions.md)
18. [Url to Image](./built-in/url_to_image.md)
19. [List Task](./built-in/list_task.md)
20. [Bypass](./built-in/bypass.md)
21. [Wait Task](./built-in/wait_task.md)
22. [Workspace Read](./built-in/workspace_read.md)
23. [Workspace Write](./built-in/workspace_write.md)
24. [Workspace Delete](./built-in/workspace_delete.md)
25. [Workspace List](./built-in/workspace_list.md)
26. [Workspace Info](./built-in/workspace_info.md)
27. [Deeseek Search](./built-in/deepseek_search.md)
28. [Deeseek Fetch](./built-in/deepseek_fetch.md)

> Workspace 系列工具通过 Data Server 访问虚拟工作区。使用前需要：
> 在 `configs/project_configs/config.json` 里把 `data_server.base_url` 指向运行中的
> Data Server，并把工具名加入 `tool_calls.registed`；用户侧还要在
> `allowed_tool_calls`（或 `tool_calls.allowed_by_default`）中允许，模型才能调用。