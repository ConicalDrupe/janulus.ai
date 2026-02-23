import hashlib
from pathlib import Path

from elevenlabs import ElevenLabs
from domain.models.generated_sentence import GeneratedSentence
from domain.tts_generator import TtsGenerator


def _compute_audio_hash(L2: str, L2_text: str, voice_id: str) -> str:
    parts = [L2.strip().lower(), L2_text.strip(), voice_id.strip().lower()]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


class ElevenLabsTtsGenerator(TtsGenerator):
    def __init__(
        self,
        audio_dir: Path,
        api_key: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
    ):
        self._audio_dir = audio_dir
        self._client = ElevenLabs(api_key=api_key)
        self._voice_id = voice_id
        self._model_id = model_id

    def generate(self, sentence: GeneratedSentence) -> str:
        audio_hash = _compute_audio_hash(sentence.L2, sentence.L2_text, self._voice_id)
        output_path = self._audio_dir / f"{audio_hash}.mp3"

        if output_path.exists():
            return str(output_path)

        audio_iter = self._client.text_to_speech.convert(
            voice_id=self._voice_id,
            text=sentence.L2_text,
            model_id=self._model_id,
        )
        with open(output_path, "wb") as f:
            for chunk in audio_iter:
                f.write(chunk)

        return str(output_path)
