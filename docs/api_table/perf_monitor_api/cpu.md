# Monitor CPU Usage API

获取当前 CPU 使用率。

- **`/perf_monitor/cpu`**
  - **Method:** `GET`
  - **Query Parameters:**
    - `interval` (optional): 查询的时间间隔，单位为秒，默认为 1 秒。
    - `percpu` (optional): 是否返回每个核心的使用率，默认为 `false`。
  - **Response:**
    - `cores` (int | null): 当前 CPU 的物理核心数。
    - `logical_cores` (int | null): 当前 CPU 的逻辑核心数。
    - `percent` (float | list[float]): 当前 CPU 的使用率，如果 `percpu` 为 `true`，则返回每个核心的使用率列表，否则返回一个浮点数表示总的使用率。