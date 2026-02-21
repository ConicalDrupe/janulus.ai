from pydantic import BaseModel, Field


class GeminiSentenceValidater(BaseModel):
    is_used: bool = Field(description="A boolean value indicating wheather native speakers use this sentence")
