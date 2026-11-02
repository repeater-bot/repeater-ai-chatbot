# Part Of Context

获取指定时间内的用户上下文

- **`/userdata/context/part_of/{user_id}-{begin}-{end}`**
- **`/userdata/context/part_of/{user_id}-{begin}-{end}.json`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `JSON列表`
    - **Content:**
      - *\*参考[Context](./../../user_data_type.md#context)*