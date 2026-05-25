from typing import Protocol


class ImageStorage(Protocol):
    def upload(self, data: bytes, folder: str, filename: str) -> str:
        """Store image bytes and return a URL accessible by the client."""
        ...
