# Get Config API

获取指定用户的配置

- **`/userdata/config/get/{user_id:str}`**
- **`/userdata/config/get/{user_id:str}.json`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `Text`
    - **Content:**
      - *\*当前用户设置的提示词*