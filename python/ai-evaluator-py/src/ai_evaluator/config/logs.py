"""Logging configuration for the application."""

import logging
import logging.config
from dataclasses import dataclass, field


@dataclass
class LoggingConfig:
    """Logging Configuration class."""

    name: str = field(default="semantic_kernel_sampler")

    config_path: str = field(default_factory=lambda: "config/logging.conf")

    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance for this configuration."""
        return logging.getLogger(self.name)

    def __post_init__(self) -> None:
        """Post-initialization to set up logging configuration."""
        logging.config.fileConfig(self.config_path)
        self.logger.debug("Loaded logging configuration from %s", self.config_path)


def run(logger: logging.Logger) -> None:  # pragma: no cover
    """Runner function."""
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")


def main() -> None:  # pragma: no cover
    """Run the main function."""
    logging_config = LoggingConfig()
    logger: logging.Logger = logging_config.logger

    logger.info("Running main.")
    run(logger)


if __name__ == "__main__":  # pragma: no cover
    main()
