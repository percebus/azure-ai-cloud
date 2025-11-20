from typing import Optional

from pydantic import BaseModel, Field


# Using Azure AI Foundry Hub
class AzureAIHubProjectSettings(BaseModel):
    subscription_id: str = Field(min_length=2)

    resource_group_name: str = Field(min_length=2)

    project_name: str = Field(min_length=2)

    # XXX? info can be inferred from above settings
    endpoint: Optional[str] = Field(default=None)
