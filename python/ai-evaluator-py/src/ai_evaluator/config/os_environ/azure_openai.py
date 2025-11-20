from pydantic import BaseModel, Field


class AzureOpenAISettings(BaseModel):
    base_url: str = Field()

    # XXX: Use AIProjectClient
    api_key: str = Field()

    deployment_name: str = Field()

    api_version: str = Field()
