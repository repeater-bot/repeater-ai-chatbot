# Monitor Memory Usage API

获取当前 Memory 使用率。

- **`/perf_monitor/memory`**
  - **Method:** `GET`
  - **Response:**
    - `virtual_memory`: 当前虚拟内存使用率。
      - `total_size`: 总大小。
      - `available_size`: 可用大小。
      - `used_size`: 已使用大小。
      - `percent`: 使用率。
    - `swap_memory`: 当前交换内存使用率。
      - `total_size`: 总大小。
      - `free_size`: 可用大小。
      - `used_size`: 已使用大小。
      - `percent`: 使用率。
