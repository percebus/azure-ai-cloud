"""GroundTruth file loader."""

from pathlib import Path
from typing import Generator, Iterable, Optional, Protocol

from a2a_prompt_runner.models.dataset import DatasetModel


class DatasetLoaderProtocol(Protocol):
    """DatasetLoaderProtocol Protocol."""

    file_name: str

    folder: str

    @property
    def data(self) -> list[DatasetModel]:
        """Return the items from the dataset_loader."""
        ...

    @property
    def file_path(self) -> Path:
        """Return the path to the downloaded file."""
        ...

    @classmethod
    def read_from_jsonl_file(cls, file_path: Path) -> Generator[tuple[int, str], None, None]:
        """Read a JSONL file and yields tuples of (line_number, json_string) for each non-empty line."""
        ...

    @classmethod
    def load_from_jsonl_file(cls, file_path: Path) -> Iterable[DatasetModel]:
        """
        Load ground truth records from a JSONL file.

        Returns a list of DatasetModel instances for valid lines, skipping any malformed entries.
        """
        ...

    def load_from_local_jsonl_file(self, file_name: Optional[str] = None) -> Iterable[DatasetModel]:
        """Load a JSONL file from a local file."""
        ...

    def download_jsonl_file(self, file_name: Optional[str] = None) -> None:
        """Download a file from a remote location."""
        ...

    def load_from_remote_jsonl_file(self, file_name: Optional[str] = None) -> Iterable[DatasetModel]:
        """Download a JSONL file from a remote location and loads the ground truth records."""
        ...
