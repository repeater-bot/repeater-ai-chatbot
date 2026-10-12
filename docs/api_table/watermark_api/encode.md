# Watermark Encode API

向图片中添加不可见水印

- **`/watermark/encode`**
  - **Requset**
    - **method:** `POST`
    - **type:** `JSON`
    - **Content:**
      - `image` (str): 图片的 URL（不支持内网地址）
      - `text` (str): 水印的文本
  - **Response**
    - **type:** `Image`
    - **Content:**
      - *\*添加水印后的图片*