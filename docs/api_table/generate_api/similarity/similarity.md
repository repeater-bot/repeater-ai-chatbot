# Calculate Similarity

计算两个文本的相似度

- **`/generate/similarity/{user_id:str}`**
  - **Requset**
    - **method:** `POST`
    - **type:** `JSON`
    - **Content:**
      - `model_id` (str | list[str]): 模型 ID
      - `first_text` (str): 第一个提示词
      - `second_text` (str): 第二个提示词
  - **Response**
    - **type:** `JSON`
    - **Content:**
      - `similarity` (float): 相似度
      - `first_text` (str): 第一个提示词
      - `second_text` (str): 第二个提示词