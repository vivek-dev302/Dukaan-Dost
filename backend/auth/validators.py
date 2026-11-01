"""Request and response schemas for authentication."""

from pydantic import BaseModel, Field


class GoogleCredential(BaseModel):
    credential: str = Field(min_length=100, max_length=8192)
