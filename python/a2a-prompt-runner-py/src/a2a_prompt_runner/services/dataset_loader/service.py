"""Dataset file loader."""

import logging
import os
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Generator, Iterable, Optional, Tuple

# from azure.storage.blob import ContainerClient, StorageStreamDownloader  # TODO
from opentelemetry import metrics, trace
from opentelemetry.trace import Span, Status, StatusCode
from pydantic import ValidationError

from a2a_prompt_runner.models.dataset import DatasetModel
from a2a_prompt_runner.services.dataset_loader.protocol import DatasetLoaderProtocol

meter = metrics.get_meter(__name__)
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
dataset_loaded_counter = meter.create_counter("dataset.loaded", description="Count of dataset records loaded from file")


@dataclass
class DatasetLoader(DatasetLoaderProtocol):
    """
    DatasetLoader class for loading dataset records from a file.

    Fields:
        - file_name:str
        - items:List[DatasetModel]
    """

    # TODO
    # container_client: ContainerClient = field()

    file_name: str = field(default="")

    folder: str = field(default="./data/input")

    _items: Iterable[DatasetModel] = field(default_factory=list)  # type: ignore[assignment]

    _data: list[DatasetModel] = field(default_factory=list)  # type: ignore[assignment]

    @property
    def data(self) -> list[DatasetModel]:
        """Return the items from the dataset_loader."""
        if not self._data:
            self._data = list(self._items)

        return self._data

    @property
    def file_path(self) -> Path:
        """Return the path to the downloaded file."""
        return Path(os.path.join(self.folder, self.file_name))

    @classmethod
    def try_parse_json(cls, json_string: str, line_number: int, span: Span) -> Optional[DatasetModel]:
        """
        Attempt to parse a JSON string into a Dataset instance.

        If validation fails, logs the error, records it in the span, and returns None.
        """
        try:
            return DatasetModel.model_validate_json(json_string)

        except ValidationError as ve:
            logger.error("Validation error in line %d: %s; error: %s", line_number, json_string.strip(), ve)
            span.record_exception(ve)
            return None

    @classmethod
    def read_from_jsonl_file(cls, file_path: Path) -> Generator[Tuple[int, str], None, None]:
        """Read a JSONL file and yields tuples of (line_number, json_string) for each non-empty line."""
        with tracer.start_as_current_span("DatasetLoader.read_from_jsonl_file"), open(file_path, "r", encoding="utf-8") as file:
            for idx, line in enumerate(file, start=1):
                if line.strip():
                    yield idx, line

    @classmethod
    def load_from_jsonl_file(cls, file_path: Path) -> Iterable[DatasetModel]:
        """
        Load dataset records from a JSONL file.

        Returns a list of Dataset instances for valid lines, skipping any malformed entries.
        """
        logger.info("Starting to load dataset records from file: %s", file_path)
        with tracer.start_as_current_span("DatasetLoader.load_from_jsonl_file") as span:
            try:
                for idx, json_string in cls.read_from_jsonl_file(file_path):
                    dataset: Optional[DatasetModel] = cls.try_parse_json(json_string, idx, span)
                    if dataset is not None:
                        dataset_loaded_counter.add(1)
                        yield dataset

            except FileNotFoundError as fnf_error:
                logger.exception("File not found: %s", file_path)
                span.record_exception(fnf_error)
                span.set_status(Status(StatusCode.ERROR, f"File not found: {file_path}"))
                raise fnf_error

            except Exception as e:
                logger.exception("An unexpected error occurred while loading file: %s", file_path)
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise e

            logger.info("Successfully loaded dataset records from file: %s", file_path)

    def load_from_local_jsonl_file(self, file_name: Optional[str] = None) -> Iterable[DatasetModel]:
        """
        Load dataset records from a JSONL file.

        Returns a list of Dataset instances for valid lines, skipping any malformed entries.
        """
        with tracer.start_as_current_span("DatasetLoader.load_from_local_jsonl_file"):
            if file_name:
                logger.debug("Setting file_name to: %s", file_name)
                self.file_name = file_name

            logger.info("Loading dataset records from file: %s", self.file_name)
            self._items = DatasetLoader.load_from_jsonl_file(self.file_path)
            return self._items

    def download_jsonl_file(self, file_name: Optional[str] = None) -> None:
        """
        Load dataset records from the file specified in `file_name` and stores them in the instance's `items` attribute.

        Automatically determines the file type based on extension.
        """
        raise NotImplementedError("Azure Blob Storage functionality is not implemented yet.")

        # TODO
        # with tracer.start_as_current_span("DatasetLoader.load_from_remote_jsonl_file"):
        #     if file_name:
        #         logger.debug("Setting file_name to: %s", file_name)
        #         self.file_name = file_name

        #     downloader: StorageStreamDownloader[bytes] = self.container_client.download_blob(self.file_name)
        #     contents: bytes = downloader.readall()

        #     logger.info("Loading dataset records from file: %s", self.file_name)
        #     logger.debug("Creating folder: %s", self.folder)
        #     Path(self.folder).mkdir(parents=True, exist_ok=True)

        #     logger.debug("Writing file to: %s", self.file_path)
        #     with open(file=self.file_path, mode="wb") as file:
        #         file.write(contents)

        #     logger.info("Downloaded file to: %s", self.file_path)

    def load_from_remote_jsonl_file(self, file_name: Optional[str] = None) -> Iterable[DatasetModel]:
        """
        Load dataset records from a JSONL file.

        Returns a list of Dataset instances for valid lines, skipping any malformed entries.
        """
        with tracer.start_as_current_span("DatasetLoader.load_from_remote_jsonl_file"):
            if file_name:
                logger.debug("Setting file_name to: %s", file_name)
                self.file_name = file_name

            logger.info("Downloading file %s into %s", self.file_name, self.folder)

            if not self.file_path.exists():
                logger.info("File %s does not exist. Downloading...", self.file_path)
                self.download_jsonl_file()
                logger.info("Downloaded file %s", self.file_path)

            logger.info("Loading dataset records from file: %s", self.file_path)
            return self.load_from_local_jsonl_file()

    def __repr__(self) -> str:  # pragma: no cover
        """Represent a DatasetLoader instance."""
        top_items: Iterable[DatasetModel] = islice(self.data, 3)
        represented_items: Iterable[str] = map(str, top_items)
        return "\n".join(represented_items)
