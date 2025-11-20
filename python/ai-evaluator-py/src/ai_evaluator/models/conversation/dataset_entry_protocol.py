from typing import Protocol

from ai_evaluator.models.conversation.conversation import ConversationProtocol


class DatasetEntryProtocol(Protocol):
    conversation: ConversationProtocol
