# Monitor Disk Usage API

获取当前 Disk 使用率。

- **`/perf_monitor/disk`**
  - **Method:** `GET`
  - **Query Parameters:**
    - `all_partitions` (optional): 是否获取所有分区信息，默认为 `false`。
  - **Response:**
    - `partitions` 当前磁盘使用情况列表。
      - *\*For each partition*
        - `device`: 设备名称
        - `mountpoint`: 挂载点
        - `fstype`: 文件系统类型
        - `opts`: 挂载选项
        - `usage`: 使用率，单位为百分比
          - `total`: 总大小
          - `used`: 已使用大小
          - `free`: 可用大小
          - `percent`: 使用率