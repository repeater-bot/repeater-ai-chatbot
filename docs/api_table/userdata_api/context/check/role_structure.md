# Check Role Structure API

检查上下文中的角色结构是否符合 user - assistant 的结构

- **`/userdata/context/structure_check/role/{user_id:str}`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `JSON`
    - **Response Body:**
      - `message` (str): 错误信息
      - `index` (int): 错误的上下文索引
      - `role` (str): 错误的上下文角色
      - `expected_role` (str): 预期的上下文角色

如果没有错误，索引会返回 `-1`