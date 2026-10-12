# Vectors API

计算文本的向量表示

- **`/generate/vectors/{user_id:str}`**
  - **Requset**
    - **method:** `POST`
    - **type:** `JSON`
    - **Content:**
      - `model` (str | list[str]): 模型 ID (可选)
      - `texts` (list[str]): 输入文本
  - **Response**
    - **type:** `JSON`
    - **Content:**
      - `vectors` (list[list[float]]): 向量表示