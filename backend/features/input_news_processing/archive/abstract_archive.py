import abc
from typing import Optional


class AbstractArchive(abc.ABC):
    def save_file(
        self,
        file_content: bytes,
        suffix: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        pass

    def get_file(self, path: str) -> bytes:
        pass
