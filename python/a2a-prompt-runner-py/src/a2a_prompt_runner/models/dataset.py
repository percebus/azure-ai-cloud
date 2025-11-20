from typing import Optional

from pydantic import BaseModel, Field


class DatasetModel(BaseModel):
    query: str = Field(..., description="The input query or prompt.")

    ground_truth: str = Field(..., description="The expected or correct response for the given query.")

    context: Optional[str] = Field(None, description="Optional additional context for the query.")
