"""Shared Configuration Module."""

from dataclasses import dataclass, field
from typing import Any, Optional

from ai_evaluator.config.logs import LoggingConfig
from ai_evaluator.config.os_environ.settings import Settings


@dataclass
class Configuration:
    """Shared configuration model for the application."""

    settings: Settings = field(default_factory=Settings)  # type: ignore[assignment]  # FIXME

    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def debug(self) -> bool:
        """Return True if the environment is 'dev' or 'test', otherwise False."""
        return self.settings.debug

    def safe_model_dump(self) -> Optional[dict[str, Any]]:
        """Safely dump the model to a dictionary, ignoring any errors."""
        return self.settings.model_dump() if self.settings.debug else None
