from django.conf import settings
from .base import ImageStorage
from .s3 import S3ImageStorage
from .local import LocalImageStorage


def get_storage() -> ImageStorage:
    backend = getattr(settings, "IMAGE_STORAGE_BACKEND", "local")
    if backend == "s3":
        return S3ImageStorage()
    if backend == "local":
        return LocalImageStorage()
    raise ValueError(f"Unknown IMAGE_STORAGE_BACKEND: {backend!r}. Choose 's3' or 'local'.")
