import time
import boto3
from django.conf import settings
from .base import ImageStorage


class S3ImageStorage:
    def upload(self, data: bytes, folder: str, filename: str) -> str:
        key = f"pixone/{folder}/{int(time.time())}_{filename}"
        boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        ).put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=data,
            ContentType="image/jpeg",
        )
        return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


_: ImageStorage = S3ImageStorage()
