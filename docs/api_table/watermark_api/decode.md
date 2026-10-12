# Watermark Decode API

从图片中提取水印文本

- **`/watermark/decode`**
  - **Requset**
    - **method:** `POST`
    - **type:** `JSON`
    - **Content:**
      - `image` (str): 图片的 URL（不支持内网地址）
  - **Response**
    - **type:** `Text`
    - **Content:**
      - *\*水印的文本*