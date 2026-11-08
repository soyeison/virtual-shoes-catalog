from abc import ABC, abstractmethod


class FileStoragePort(ABC):
    @abstractmethod
    def upload_image(self, file_name: str, file_bytes: bytes, content_type: str) -> str:
        pass
