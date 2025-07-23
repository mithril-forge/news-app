import abc
import pathlib
from typing import Optional


class AbstractArchive(abc.ABC):
    @abc.abstractmethod
    def save_file(
            self,
            file_content: bytes,
            suffix: Optional[str] = None,
            name: Optional[str] = None,
    ) -> str | pathlib.Path:
        pass

    @abc.abstractmethod
    def get_file(self, path: str | pathlib.Path) -> bytes:
        pass
