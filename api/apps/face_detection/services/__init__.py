from django.conf import settings
from .base import FaceDetector, FaceRect
from .rekognition import RekognitionFaceDetector
from .own import OwnFaceDetector


def get_detector() -> FaceDetector:
    backend = getattr(settings, "FACE_DETECTOR_BACKEND", "rekognition")
    if backend == "rekognition":
        return RekognitionFaceDetector()
    elif backend == "own":
        return OwnFaceDetector()
    raise ValueError(f"Unknown FACE_DETECTOR_BACKEND: {backend}")