# Request Log

## Request Log Object

[Request Log Object](./request_log_object.md)是一个用于记录请求日志的对象，
记录了单次请求中的时间与Token信息，
以便于后续对额度支出与性能进行分析。

## Request Log API

用于获取[Request Log Object](./request_log_object.md)
分为[流式](./apis/stream.md)与[非流式](./apis/non_steram.md)两种方式。
其中，[流式接口](./apis/stream.md)会每读取一条就返回一条，返回格式是JSONL，
而[非流式接口](./apis/non_steram.md)则会先将所有日志读取进缓冲区后再用JSON格式返回。