import hashlib
import wave
from pathlib import Path

from domain.models.generated_sentence import GeneratedSentence
from domain.tts_generator import TtsGenerator
from google import genai
from google.genai import types


def _compute_audio_hash(L2: str, L2_text: str, voice_name: str) -> str:
    parts = [L2.strip().lower(), L2_text.strip(), voice_name.strip().lower()]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _write_wav(path: Path, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


# Hyphens in the path prevent a standard import; load with importlib at module level.
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location(
    "plain_lang_bcp47",
    Path(__file__).parent / "lang-lookups" / "plain-lang-to-bcrp-47.py",
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
plain_language_to_bcp47: dict[str, str] = _mod.plain_language_to_bcp47


class GeminiTtsGenerator(TtsGenerator):
    def __init__(
        self,
        audio_dir: Path,
        client: genai.Client,
        voice_name: str = "Kore",
        model_id: str = "gemini-2.5-flash-tts",
        director_prompt: str = "Clearly pronounce: ",
    ):
        self._audio_dir = audio_dir
        self._client = client
        self._voice_name = voice_name
        self._model_id = model_id
        self._director_prompt = director_prompt

    def generate(self, sentence: GeneratedSentence) -> str:
        language_code = plain_language_to_bcp47[sentence.L2.strip().title()]
        audio_hash = _compute_audio_hash(sentence.L2, sentence.L2_text, self._voice_name)
        output_path = self._audio_dir / f"{audio_hash}.wav"

        if output_path.exists():
            return str(output_path)

        contents = self._director_prompt + sentence.L2_text
        response = self._client.models.generate_content(
            model=self._model_id,
            contents=contents,
            config=types.GenerateContentConfig(
                speech_config=types.SpeechConfig(
                    language_code=language_code,
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self._voice_name,
                        )
                    ),
                ),
                temperature=2.0,
            ),
        )

        pcm = response.candidates[0].content.parts[0].inline_data.data
        _write_wav(output_path, pcm)
        return str(output_path)
