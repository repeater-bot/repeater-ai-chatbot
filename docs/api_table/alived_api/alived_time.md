# Alived Time API

检测后端服务器本次持续运行的时间。

- **`/alived/time`**
- **`/alived/time/s`**
  - **Request**
    - **method:** `GET`
  - **Response**
    - **type:** `Number`
    - **Content**: 
      - *\*后端的运行秒数*

- **`/alived/time/ms`**
  - **Request**
    - **method:** `GET`
  - **Response**
    - **type:** `Number`
    - **Content**: 
      - *\*后端的运行毫秒数*

- **`/alived/time/us`**
  - **Request**
    - **method:** `GET`
  - **Response**
    - **type:** `Number`
    - **Content**: 
      - *\*后端的运行微秒数*

- **`/alived/time/ns`**
  - **Request**
    - **method:** `GET`
  - **Response**
    - **type:** `Number`
    - **Content**: 
      - *\*后端的运行纳秒数*
