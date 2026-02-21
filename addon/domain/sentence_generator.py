from abc import ABC, abstractmethod

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions
from domain.models.vocab_list import VocabList


class SentenceGenerator(ABC):

    @abstractmethod
    def generate_all_sentence(self, vocab: VocabList, grammar_options_list: list[GrammarOptions]) -> list[GeneratedSentence]:
        pass

    @abstractmethod
    def generate_sentence(
        self, nouns: list[str], verb: str, grammar_options: GrammarOptions
    ) -> GeneratedSentence:
        pass
