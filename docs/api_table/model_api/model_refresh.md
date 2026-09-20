# Model Refresh

刷新模型池中的模型信息

- **`/model_refresh/{provider_id: str}`**
  - **method**: `POST`
  - **Response**
    - **type:** `JSON`
    - **Content:**
      - `message` (str): 状态信息(成功情况下永远为 "Models refreshed successfully")
      - `status` (str): 状态码(成功情况下永远为 "success")