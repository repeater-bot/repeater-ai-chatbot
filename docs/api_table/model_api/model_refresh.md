# Model Refresh

刷新模型池中的模型信息

- **`/model_refresh`**
- **`/model_refresh/{provider_id: str}`**
  - **method**: `POST`
  - **Response**
    - **type:** `JSON`
    - **Content:**
      - `message` (str): 状态信息(成功情况下永远为 "Models refreshed successfully")
      - `status` (str): 状态码(成功情况下永远为 "success")

当不传入 `provider_id` 时，将刷新所有供应商的模型信息