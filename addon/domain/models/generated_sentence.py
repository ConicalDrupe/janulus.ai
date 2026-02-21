from dataclasses import dataclass

from domain.models.grammar_options import GrammarOptions


@dataclass
class GeneratedSentence:
    L1: str  # primary language code
    L2: str  # target language code
    L1_text: str  # primary language
    L2_text: str  # target language
    grammar_options: GrammarOptions
