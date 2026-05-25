from .base import FaceDetector, FaceRect


class OwnFaceDetector:
    """
    Placeholder for our own face detection model.
    Will be implemented using OpenCV / MediaPipe / ONNX.
    """

    def detect(self, image_bytes: bytes) -> list[FaceRect]:
        raise NotImplementedError("Own face detector is not implemented yet.")


_: FaceDetector = OwnFaceDetector()