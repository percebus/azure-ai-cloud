from typing import Optional, Protocol


class MessageProtocol(Protocol):
    role: str

    content: str

    context: Optional[str]
