from abc import ABC, abstractmethod

from domain.models.generated_sentence import GeneratedSentence


class SentenceRepository(ABC):
    @abstractmethod
    def save(self, sentence: GeneratedSentence) -> None:
        """Persist sentence with is_valid=NULL. Raises ValueError if already cached."""

    @abstractmethod
    def find(self, sentence: GeneratedSentence) -> tuple[GeneratedSentence, bool | None] | None:
        """
        Look up by hash(L1, L2, L2_text).
        Hit: (sentence, is_valid) — is_valid is None/True/False.
        Miss: None.
        Caller skips entries where is_valid is False (rejected).
        """

    @abstractmethod
    def find_rejected(self) -> list[GeneratedSentence]:
        """All sentences with is_valid=False."""

    @abstractmethod
    def mark_valid(self, sentence: GeneratedSentence) -> None:
        """Set is_valid=True and validated_at=now."""

    @abstractmethod
    def mark_rejected(self, sentence: GeneratedSentence) -> None:
        """Set is_valid=False and validated_at=now."""

    @abstractmethod
    def set_audio_path(
        self,
        sentence: GeneratedSentence,
        audio_path: str,
        voice_name: str,
        voice_model: str,
    ) -> None:
        """Attach audio metadata and audio_set_at=now."""
