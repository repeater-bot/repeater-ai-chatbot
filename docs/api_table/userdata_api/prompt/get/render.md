# Render Prompt API

渲染提示词模板

- **`/userdata/prompt/render/{user_id:str}`**
- **`/userdata/prompt/render/{user_id:str}.md`**
  - **Requset**
    - **method:** `GET`
    - **Query:**
      - `branch_id` (str): 分支ID，如果为空则使用活动分支
  - **Response**
    - **type:** `Text`
    - **Content:**
      - *\*提交给 AI 的提示词*

当用户未设置提示词时
该接口会自动去全局默认提示词中寻找模板
最终返回的就是当前用户发起生成请求时
提交给 AI 的提示词