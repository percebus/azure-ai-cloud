from typing import Optional, Protocol


class GroundTruthEntryProtocol(Protocol):
    query: str

    ground_truth: str

    context: Optional[str] = None
