# Monitor Network Usage API

获取当前 Network 使用率。

- **`/perf_monitor/network`**
  - **Method:** `GET`
  - **Response:**
    - `net_io_counters`: 网络 IO 计数器。
      - *\*网卡名称*
        - `bytes_sent`: 发送的字节数。
        - `bytes_recv`: 接收的字节数。
        - `packets_sent`: 发送的包数。
        - `packets_recv`: 接收的包数。
        - `errin`: 接收错误数。
        - `errout`: 发送错误数。
        - `dropin`: 接收丢弃的包数。
        - `dropout`: 发送丢弃的包数。
    - `net_connections`: 当前网络连接列表。
      - *\*PID(可能为空)*
        - `fd`: 文件描述符。
        - `pid`: 进程 ID。
        - `status`: 连接状态。