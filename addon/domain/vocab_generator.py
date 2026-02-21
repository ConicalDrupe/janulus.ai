from abc import ABC, abstractmethod

from domain.models.vocab_list import VocabList
from domain.models.user_qa import UserQA

class VocabGenerator(ABC):

    @abstractmethod
    def generate_vocab(self, userqa: UserQA) -> list[VocabList]:
        pass

        