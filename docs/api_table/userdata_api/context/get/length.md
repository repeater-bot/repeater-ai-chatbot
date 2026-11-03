# Get Context Length Info API

获取指定用户的上下文长度信息

- **`/userdata/context/length/{user_id:str}`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `JSON`
    - **Content:**
      - `total_context_length` (int): 上下文字符数量
      - `context_length` (int): 上下文对话条目数量
      - `average_content_length` (float): 平均上下文长度