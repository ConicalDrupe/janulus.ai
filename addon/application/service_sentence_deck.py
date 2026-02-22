from domain.models.deck import Deck, build_deck_name
from domain.models.deck_entry import DeckEntry
from domain.models.grammar_options import GrammarOptions
from domain.models.vocab_list import VocabList
from domain.sentence_generator import SentenceGenerator
from domain.tts_generator import TtsGenerator


class SentenceDeckService:
    def __init__(
        self,
        generator: SentenceGenerator,
        tts: TtsGenerator | None = None,
    ) -> None:
        self._generator = generator
        self._tts = tts

    async def build_deck(
        self,
        vocab: VocabList,
        L1: str,
        L2: str,
        grammar_options_list: list[GrammarOptions],
        with_audio: bool,
    ) -> Deck:
        sentences = await self._generator.generate_all_sentence(
            vocab, L2, grammar_options_list
        )

        # Derive a representative tense/type for the deck name (use first options entry)
        first_opts = grammar_options_list[0] if grammar_options_list else None
        tense = first_opts.tense if first_opts else None
        sentence_type = first_opts.sentence_type if first_opts else None

        entries: list[DeckEntry] = []
        for sentence in sentences:
            audio_path: str | None = None
            if with_audio and self._tts is not None:
                audio_path = self._tts.generate(sentence)

            tags: list[str] = [
                sentence.grammar_options.tense.value,
            ]
            if sentence.grammar_options.sentence_type:
                tags.append(sentence.grammar_options.sentence_type.value)
            if audio_path:
                tags.append("audio")

            entries.append(
                DeckEntry(
                    primary_language_code=L1,
                    foreign_language_code=L2,
                    primary_text=sentence.L1_text,
                    foreign_text=sentence.L2_text,
                    audio_path=audio_path,
                    tags=tags,
                )
            )

        name = build_deck_name(L2, with_audio and self._tts is not None, tense, sentence_type)
        return Deck(name=name, entries=entries)
