from abc import ABC, abstractmethod

from domain.models.generated_sentence import GeneratedSentence


class TtsGenerator(ABC):
    @abstractmethod
    def generate(self, sentence: GeneratedSentence) -> str:
        """Generate TTS audio for the L2 text of a sentence.

        Saves the audio file and returns its absolute path as a string.
        """
