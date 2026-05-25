import io
import boto3
from PIL import Image
from django.conf import settings
from .base import FaceDetector, FaceRect


class RekognitionFaceDetector:
    def __init__(self):
        self.client = boto3.client(
            "rekognition",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def detect(self, image_bytes: bytes) -> list[FaceRect]:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img_width, img_height = img.size

        response = self.client.detect_faces(
            Image={"Bytes": image_bytes},
            Attributes=["DEFAULT"],
        )

        faces = []
        for face in response.get("FaceDetails", []):
            box = face["BoundingBox"]
            x = int(box["Left"] * img_width)
            y = int(box["Top"] * img_height)
            width = int(box["Width"] * img_width)
            height = int(box["Height"] * img_height)
            confidence = face["Confidence"]
            landmarks = {
                lm["Type"]: {"x": int(lm["X"] * img_width), "y": int(lm["Y"] * img_height)}
                for lm in face.get("Landmarks", [])
            }
            faces.append(FaceRect(x=x, y=y, width=width, height=height, confidence=confidence, landmarks=landmarks))

        return faces


_: FaceDetector = RekognitionFaceDetector()