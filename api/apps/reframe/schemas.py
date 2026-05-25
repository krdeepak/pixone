from enum import Enum
from ninja import Schema


class ReframeParams(Schema):
    x: int
    y: int
    width: int
    height: int
    output_width: int | None = None
    output_height: int | None = None
    image_url: str | None = None


class SmartReframeMode(str, Enum):
    ZOOMED = "zoomed"
    STANDARD = "standard"
    FULL = "full"


class SmartReframeParams(Schema):
    mode: SmartReframeMode = SmartReframeMode.STANDARD
    aspect_ratio: str = "1:1"
    image_url: str | None = None


class ReframeResponse(Schema):
    request_id: int
    output_url: str
    metadata: dict


class SmartReframeResponse(Schema):
    request_id: int
    output_url: str
    face_count: int
    mode: str
    metadata: dict
