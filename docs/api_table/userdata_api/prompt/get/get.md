# Get Prompt API

从当前用户获取提示词内容

- **`/userdata/prompt/get/{user_id:str}`**
- **`/userdata/prompt/get/{user_id:str}.md`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `Text`
    - **Content:**
      - *\*当前用户设置的提示词*

如果用户使用的是默认提示词
则返回的是一个空字符串