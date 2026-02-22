from abc import ABC, abstractmethod


class VocabRepository(ABC):
    @abstractmethod
    def save(self, L1: str, L2: str, L1_text: str, L2_text: str) -> None:
        """Cache a word translation. Raises ValueError if already cached."""

    @abstractmethod
    def find(self, L1: str, L2: str, L1_text: str) -> str | None:
        """Return L2_text translation, or None on cache miss."""

    @abstractmethod
    def set_audio_path(
        self,
        L1: str,
        L2: str,
        L1_text: str,
        audio_path: str,
        voice_name: str,
        voice_model: str,
    ) -> None:
        """Attach TTS audio to a cached word translation."""
