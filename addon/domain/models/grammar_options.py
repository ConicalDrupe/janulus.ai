from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tense(Enum):
    # Present
    SIMPLE_PRESENT = "simple_present"  # I walk
    PRESENT_CONTINUOUS = "present_continuous"  # I am walking
    PRESENT_PERFECT = "present_perfect"  # I have walked
    PRESENT_PERFECT_CONTINUOUS = "present_perfect_continuous"  # I have been walking

    # Past
    SIMPLE_PAST = "simple_past"  # I walked
    PAST_CONTINUOUS = "past_continuous"  # I was walking
    PAST_PERFECT = "past_perfect"  # I had walked
    PAST_PERFECT_CONTINUOUS = "past_perfect_continuous"  # I had been walking

    # Continuous (Progressive)
    SIMPLE_FUTURE = "simple_future"  # I will walk
    FUTURE_CONTINUOUS = "future_continuous"  # I will be walking
    FUTURE_PERFECT = "future_perfect"  # I will have walked
    FUTURE_PERFECT_CONTINUOUS = "future_perfect_continuous"  # I will have been walking


class SentenceType(Enum):
    DECLARATIVE = "declarative"
    INTERROGATIVE = "interrogative"
    EXCLAMATORY = "exclamatory"
    IMPERATIVE = "imperative"


class GrammaticalNumber(Enum):
    SINGULAR = "singular"
    PLURAL = "plural"


@dataclass
class GrammarOptions:
    tense: Tense
    sentence_type: Optional[SentenceType]
    grammatical_number: Optional[GrammaticalNumber]
    include_preposition: bool
    include_possession: bool
