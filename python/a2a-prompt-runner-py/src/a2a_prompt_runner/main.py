import asyncio
import logging
from typing import Any
from uuid import uuid4

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest, SendMessageResponse
from httpx import AsyncClient, Timeout

from a2a_prompt_runner.dependency_injection.container import container
from a2a_prompt_runner.services.dataset_loader.protocol import DatasetLoaderProtocol

# Configure logging to show INFO level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Get a logger instance


# SRC: https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/test_client.py
async def main_async() -> None:
    # TODO read from .env
    base_url = "http://localhost:9999"

    dataset_filename = "hi_and_temperature.jsonl"

    dataset_loader = container[DatasetLoaderProtocol]  # pyright: ignore[reportAssignmentType]
    dataset_loader.file_name = dataset_filename
    dataset_loader.load_from_local_jsonl_file()

    timeout = container[Timeout]
    async with AsyncClient(timeout=timeout, headers={"X-Reference": dataset_filename}) as httpx_client:
        # Initialize A2ACardResolver
        a2a_card_resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )

        agent_card: AgentCard | None = None
        agent_card = await a2a_card_resolver.get_agent_card()
        a2a_client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        uuid = uuid4()

        for dataset in dataset_loader.data:
            print(f"Processing: '{dataset}'")
            send_message_payload: dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": dataset.query}],
                    "messageId": uuid.hex,
                },
            }

            print("Sending...")
            request = SendMessageRequest(id=str(uuid), params=MessageSendParams(**send_message_payload))
            response: SendMessageResponse = await a2a_client.send_message(request)
            json_response: dict[str, Any] = response.model_dump(mode="json", exclude_none=True)
            first_part = json_response["result"]["parts"][0]
            print(first_part["text"])


if __name__ == "__main__":
    asyncio.run(main_async())
