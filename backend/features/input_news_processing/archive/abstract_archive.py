import abc
import pathlib


class AbstractArchive(abc.ABC):
    @abc.abstractmethod
    def save_file(
        self,
        file_content: bytes,
        suffix: str | None = None,
        name: str | None = None,
    ) -> str | pathlib.Path:
        pass

    @abc.abstractmethod
    def get_file(self, path: pathlib.Path) -> bytes:
        pass
