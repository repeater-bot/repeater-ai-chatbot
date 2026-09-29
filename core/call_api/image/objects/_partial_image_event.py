from pydantic import BaseModel, ConfigDict
from typing import Literal

# 注意：请求侧需传 ImageSize 这类枚举（SDK 入参为严格 Literal），
# 但响应侧不做校验，服务端可能返回当前 SDK 未声明的取值。
# 为保证已生成图片能正常落盘，此处按 str 接收，避免对象化时报错丢片。

class PartialImageEvent(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    b64_json: str | None = None
    background: str | None = None
    created_at: int | None = None
    output_format: str | None = None
    partial_image_index: int | None = None
    quality: str | None = None
    size: str | None = None
    type: Literal["image_generation.partial_image"] = "image_generation.partial_image"