from abc import ABC, abstractmethod

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions
from domain.models.vocab_list import VocabList


class SentenceGenerator:

    @abstractmethod
    def generate_all_sentence(vocab: VocabList, list[GrammarOptions]) -> list[GeneratedSentences]:
        pass

    @abstractmethod
    def generate_sentence(
        nouns: str, verb: str, grammar_options: GrammarOptions
    ) -> GeneratedSentence:
        pass
