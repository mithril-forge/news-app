import datetime
import pathlib
import uuid
from typing import Optional

import structlog

from features.input_news_processing.archive.abstract_archive import AbstractArchive

logger = structlog.get_logger()


class LocalArchive(AbstractArchive):
    """Class for handling local file storage operations."""

    def __init__(self, target_location: pathlib.Path) -> None:
        """
        Initialize the LocalArchive with a target storage location.

        Args:
            target_location: Directory path where files will be stored
        """
        self.target_location = target_location
        # Ensure the target directory exists
        self.target_location.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalArchive initialized with target location: {target_location}")

    def save_file(
        self,
        file_content: bytes,
        suffix: Optional[str] = None,
        name: Optional[str] = None,
    ) -> pathlib.Path:
        """
        Save file content to the local storage.

        Args:
            file_content: Binary content of the file to save
            suffix: Optional file extension (e.g., '.txt', '.json')
            name: Optional filename, if not provided a UUID will be generated

        Returns:
            Relative path to the saved file (from the target location)
        """
        logger.debug(f"Saving file with suffix: {suffix}, name: {name}")
        if name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
            name = f"{timestamp}_{unique_id}"
            logger.debug(f"Generated filename: {name}")
        if suffix:
            if not suffix.startswith("."):
                suffix = f".{suffix}"
            filename = f"{name}{suffix}"
        else:
            filename = name

        file_path = self.target_location / filename
        file_path.write_bytes(file_content)
        logger.info(f"File saved successfully: {filename} ({len(file_content)} bytes)")
        return file_path.absolute()

    def get_file(self, path: pathlib.Path) -> bytes:
        """
        Retrieve file content from the local storage.

        Args:
            path: Relative path to the file (as returned by save_file)

        Returns:
            Binary content of the requested file

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        logger.debug(f"Retrieving file: {path}")
        if not path.is_absolute():
            absolute_path = self.target_location / path
        else:
            absolute_path = path
        if not absolute_path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        content = absolute_path.read_bytes()
        logger.info(f"File retrieved successfully: {path} ({len(content)} bytes)")
        return content
