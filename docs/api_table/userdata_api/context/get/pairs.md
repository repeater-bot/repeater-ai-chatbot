# Get Context Pair API

从当前用户获取上下文对信息

- **`/userdata/context/get_pairs/{user_id:str}`**
- **`/userdata/context/get_pairs/{user_id:str}.json`**
  - **Requset**
    - **method:** `GET`
  - **Response**
    - **type:** `JSON列表`
    - **Content:**
      - `context_pairs` (list[list[ContentUnit]]): 上下文对列表
      - `length` (int): 上下文对数量
      - `context_length` (int): 上下文长度
      - `total_character_length` (int): 总字符长度