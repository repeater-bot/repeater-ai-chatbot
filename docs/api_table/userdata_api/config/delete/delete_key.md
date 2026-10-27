# Delete Config Field API

删除指定用户配置字段

- **`/userdata/config/delkey/{user_id:str}`**
  - **Requset**
    - **method:** `PUT`
    - **type:** `FORM`
    - **Content:**
      - `key` (str):  配置字段名
  - **Response**
    - **type:** `Text`
    - **Content:**
      - *\*Config 内容*

这相当于[Set Config API](../set/set_key.md)中的
`value`参数为`null`或`type`设为`"null"`的情况