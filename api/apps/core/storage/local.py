import time
from pathlib import Path
from django.conf import settings
from .base import ImageStorage


class LocalImageStorage:
    def upload(self, data: bytes, folder: str, filename: str) -> str:
        relative = f"pixone/{folder}/{int(time.time())}_{filename}"
        dest = Path(settings.MEDIA_ROOT) / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        base = settings.BACKEND_URL.rstrip("/") if settings.BACKEND_URL else ""
        return f"{base}{settings.MEDIA_URL}{relative}"


_: ImageStorage = LocalImageStorage()
