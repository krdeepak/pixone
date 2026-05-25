from dataclasses import dataclass
from typing import Protocol


@dataclass
class FaceRect:
    x: int
    y: int
    width: int
    height: int
    confidence: float
    landmarks: dict | None = None


class FaceDetector(Protocol):
    def detect(self, image_bytes: bytes) -> list[FaceRect]:
        """Detect faces from raw image bytes and return bounding boxes."""
        ...
