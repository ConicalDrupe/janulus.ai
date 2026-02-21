from dataclasses import dataclass

from domain.models.deck_entry import DeckEntry
from domain.models.grammar_options import SentenceType, Tense


@dataclass
class Deck:
    name: str
    entries: list[DeckEntry]


def build_deck_name(
    foreign_language: str,
    has_audio: bool,
    tense: Tense | None = None,
    sentence_type: SentenceType | None = None,
) -> str:
    lang = foreign_language.lower()
    audio = "audio" if has_audio else "noaudio"
    tense_str = tense.value.lower().replace("_", "-") if tense else "mixed"
    type_str = sentence_type.value.lower().replace("_", "-") if sentence_type else "mixed"
    return f"{lang}_{audio}_{tense_str}_{type_str}"
