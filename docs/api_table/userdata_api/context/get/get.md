# Get Context API

从当前用户获取上下文信息

- **`/userdata/context/get/{user_id:str}`**
- **`/userdata/context/get/{user_id:str}.json`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `JSON列表`
    - **Content:**
      - *\*参考[Context](./../../user_data_type.md#context)*

获取当前用户所有上下文信息
注：这里头部并不会存放 `System Prompt`
它是单独存放并动态拼接的