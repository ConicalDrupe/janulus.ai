from dataclasses import dataclass


@dataclass
class DeckEntry:
    primary_language_code: str   # e.g. "en"
    foreign_language_code: str   # e.g. "hi"
    primary_text: str
    foreign_text: str
    audio_path: str | None
    tags: list[str]              # e.g. ["simple-present", "declarative", "audio"]
