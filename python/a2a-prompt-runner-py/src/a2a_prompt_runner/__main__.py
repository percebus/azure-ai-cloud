import asyncio
import logging

from a2a_prompt_runner.main import main_async

# Configure logging to show INFO level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Get a logger instance


if __name__ == "__main__":
    asyncio.run(main_async())
