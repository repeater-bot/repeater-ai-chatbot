# Get Dispatch Bots

获取客户端支持的 Bot 列表

注册名：`get_dispatch_bots`

用来在调用 `dispatch_trigger` 之前发现可用的 `bot_id`。

接受一个参数
``` json
{
  "timeout": 60 // Request timeout
}
```

返回 bot_id 列表：
``` json
{
    "bots_list": ["123456789", "987654321"] // List of bot_id
}
```
由于该工具会直接返回响应结果文本，所以此处响应格式仅供参考