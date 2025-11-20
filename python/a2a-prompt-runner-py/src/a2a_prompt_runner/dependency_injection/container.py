from httpx import Timeout
from lagom import Container

from a2a_prompt_runner.services.dataset_loader.protocol import DatasetLoaderProtocol
from a2a_prompt_runner.services.dataset_loader.service import DatasetLoader

container = Container()

# TODO? Singleton?
container[Timeout] = Timeout(60.0)

container[DatasetLoader] = lambda c: DatasetLoader()
container[DatasetLoaderProtocol] = lambda c: c[DatasetLoader]
