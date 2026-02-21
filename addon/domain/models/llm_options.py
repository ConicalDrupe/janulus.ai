from dataclasses import dataclass


@dataclass
class LLMOptions:
    model_id: str = "gemini-3-flash"
    temperature: float = 0.1
