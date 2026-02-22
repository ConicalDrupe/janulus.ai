import asyncio
import itertools
import random

from domain.models.deck import Deck, build_deck_name
from domain.models.deck_entry import DeckEntry
from domain.models.grammar_options import GrammarOptions
from domain.models.vocab_list import VocabList
from domain.repository.sentence_repository import SentenceRepository
from domain.sentence_generator import SentenceGenerator
from domain.sentence_validator import SentenceValidator
from domain.tts_generator import TtsGenerator


async def _retry_with_backoff(coro_fn, max_retries: int = 4, base_delay: float = 1.0):
    """Retry an async callable on 429/RESOURCE_EXHAUSTED with exponential backoff + jitter."""
    for attempt in range(max_retries + 1):
        try:
            return await coro_fn()
        except Exception as e:
            is_rate_limit = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
            if attempt == max_retries or not is_rate_limit:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
            await asyncio.sleep(delay)


class SentenceDeckService:
    def __init__(
        self,
        generator: SentenceGenerator,
        tts: TtsGenerator | None = None,
        sentence_repo: SentenceRepository | None = None,
        validator: SentenceValidator | None = None,
    ) -> None:
        self._generator = generator
        self._tts = tts
        self._sentence_repo = sentence_repo
        self._validator = validator

    async def build_deck(
        self,
        vocab: VocabList,
        L1: str,
        L2: str,
        grammar_options_list: list[GrammarOptions],
        with_audio: bool,
    ) -> Deck:
        nouns = list(set(vocab.subjects + vocab.objects))
        noun_pairs = [list(pair) for pair in itertools.combinations(nouns, 2)]

        all_combos = [
            (noun_pair, verb, opts)
            for opts in grammar_options_list
            for verb in vocab.verbs
            for noun_pair in noun_pairs
        ]

        # Split into cache hits and misses
        hits: list[tuple[object, list[str], str]] = []
        to_generate: list[tuple[list[str], str, GrammarOptions]] = []

        for noun_pair, verb, opts in all_combos:
            if self._sentence_repo is not None:
                result = self._sentence_repo.find(L1, L2, noun_pair, verb, opts)
                if result is not None:
                    sentence, is_valid = result
                    if is_valid is not False:
                        hits.append((sentence, noun_pair, verb))
                    continue
            to_generate.append((noun_pair, verb, opts))

        # Batch generate cache misses
        new_sentences: list[tuple[object, list[str], str]] = []
        if to_generate:
            gen_semaphore = asyncio.Semaphore(3)

            async def _guarded_generate(n, v, opts):
                async with gen_semaphore:
                    return await _retry_with_backoff(
                        lambda: self._generator.generate_sentence(
                            nouns=n, verb=v, target_language=L2, grammar_options=opts
                        )
                    )

            generated = await asyncio.gather(*[
                _guarded_generate(n, v, opts)
                for (n, v, opts) in to_generate
            ])
            for (n, v, _opts), sentence in zip(to_generate, generated):
                new_sentences.append((sentence, n, v))

        # Persist newly generated sentences
        if self._sentence_repo is not None:
            for sentence, n, v in new_sentences:
                try:
                    self._sentence_repo.save(sentence, n, v)
                except ValueError:
                    pass  # already cached (race condition)

        # Validate new sentences; exclude rejects from the deck
        if self._validator is not None:
            semaphore = asyncio.Semaphore(3)

            async def _guarded_validate(sentence):
                async with semaphore:
                    return await _retry_with_backoff(
                        lambda: self._validator.validate(sentence)
                    )

            validation_results = await asyncio.gather(*[
                _guarded_validate(sentence)
                for sentence, n, v in new_sentences
            ])
            accepted: list[tuple[object, list[str], str]] = []
            for (sentence, n, v), is_valid in zip(new_sentences, validation_results):
                if is_valid:
                    if self._sentence_repo is not None:
                        self._sentence_repo.mark_valid(sentence, n, v)
                    accepted.append((sentence, n, v))
                else:
                    if self._sentence_repo is not None:
                        self._sentence_repo.mark_rejected(sentence, n, v)
            new_sentences = accepted

        all_triples = hits + new_sentences

        # Derive deck name metadata — None collapses to "mixed" in build_deck_name
        unique_tenses = {opts.tense for opts in grammar_options_list}
        tense = next(iter(unique_tenses)) if len(unique_tenses) == 1 else None
        unique_types = {opts.sentence_type for opts in grammar_options_list}
        sentence_type = next(iter(unique_types)) if len(unique_types) == 1 else None

        voice_name = getattr(self._tts, "_voice_name", "")

        entries: list[DeckEntry] = []
        for sentence, n, v in all_triples:
            audio_path: str | None = None
            if with_audio and self._tts is not None:
                audio_path = self._tts.generate(sentence)
                if self._sentence_repo is not None:
                    self._sentence_repo.set_audio_path(sentence, n, v, audio_path, voice_name, "")

            tags: list[str] = [
                sentence.grammar_options.tense.value,
            ]
            if sentence.grammar_options.sentence_type:
                tags.append(sentence.grammar_options.sentence_type.value)
            if audio_path:
                tags.append("audio")
            tags.append(L2.strip().lower().replace(" ", "_"))

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
