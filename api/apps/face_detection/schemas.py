from ninja import Schema


class FaceRectSchema(Schema):
    x: int
    y: int
    width: int
    height: int
    confidence: float
    landmarks: dict | None = None


class FaceDetectionResponse(Schema):
    request_id: int
    faces: list[FaceRectSchema]
    face_count: int
