from abc import ABC, abstractmethod
from domain.models.generated_sentence import GeneratedSentence


class SentenceValidator(ABC):

    @abstractmethod
    async def validate(self, sentence: GeneratedSentence) -> bool:
        pass
