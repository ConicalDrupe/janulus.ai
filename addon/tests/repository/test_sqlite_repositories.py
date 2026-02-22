import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import GrammarOptions, GrammaticalNumber, SentenceType, Tense
from infrastructure.repository.sqlite_sentence_repository import SqliteSentenceRepository
from infrastructure.repository.sqlite_vocab_repository import SqliteVocabRepository


def _make_engine():
    return create_engine("sqlite:///:memory:")


def _make_sentence(L2_text: str = "मैं चलता हूँ") -> GeneratedSentence:
    grammar_options = GrammarOptions(
        tense=Tense.SIMPLE_PRESENT,
        sentence_type=SentenceType.DECLARATIVE,
        grammatical_number=GrammaticalNumber.SINGULAR,
        include_preposition=False,
        include_possession=False,
    )
    return GeneratedSentence(
        L1="english",
        L2="hindi",
        L1_text="I walk",
        L2_text=L2_text,
        grammar_options=grammar_options,
    )


def _make_sentence_no_optionals() -> GeneratedSentence:
    grammar_options = GrammarOptions(
        tense=Tense.PRESENT_CONTINUOUS,
        sentence_type=None,
        grammatical_number=None,
        include_preposition=True,
        include_possession=True,
    )
    return GeneratedSentence(
        L1="english",
        L2="hindi",
        L1_text="I am walking to the park",
        L2_text="मैं पार्क जा रहा हूँ",
        grammar_options=grammar_options,
    )


# ── Sentence repository tests ──────────────────────────────────────────────


def test_save_and_find_hit():
    repo = SqliteSentenceRepository(_make_engine())
    sentence = _make_sentence()
    repo.save(sentence)
    result = repo.find(sentence)
    assert result is not None, "Expected cache hit but got None"
    found_sentence, is_valid = result
    assert found_sentence.L1_text == sentence.L1_text
    assert found_sentence.L2_text == sentence.L2_text
    assert is_valid is None, f"Expected is_valid=None but got {is_valid}"
    print("test_save_and_find_hit passed")


def test_cache_miss_returns_none():
    repo = SqliteSentenceRepository(_make_engine())
    sentence = _make_sentence()
    result = repo.find(sentence)
    assert result is None, f"Expected None on cache miss but got {result}"
    print("test_cache_miss_returns_none passed")


def test_mark_rejected_cached():
    repo = SqliteSentenceRepository(_make_engine())
    sentence = _make_sentence()
    repo.save(sentence)
    repo.mark_rejected(sentence)
    result = repo.find(sentence)
    assert result is not None
    _, is_valid = result
    assert is_valid is False, f"Expected is_valid=False but got {is_valid}"
    rejected = repo.find_rejected()
    assert len(rejected) == 1
    assert rejected[0].L2_text == sentence.L2_text
    print("test_mark_rejected_cached passed")


def test_mark_valid_not_in_rejected():
    repo = SqliteSentenceRepository(_make_engine())
    sentence = _make_sentence()
    repo.save(sentence)
    repo.mark_valid(sentence)
    result = repo.find(sentence)
    assert result is not None
    _, is_valid = result
    assert is_valid is True, f"Expected is_valid=True but got {is_valid}"
    rejected = repo.find_rejected()
    assert len(rejected) == 0, f"Expected empty rejected list but got {rejected}"
    print("test_mark_valid_not_in_rejected passed")


def test_set_audio_path_sentence():
    engine = _make_engine()
    repo = SqliteSentenceRepository(engine)
    sentence = _make_sentence()
    repo.save(sentence)
    repo.set_audio_path(sentence, "/tmp/audio.mp3", "en-US-Wavenet-A", "tts-v2")
    from infrastructure.models.db_sentence import DbSentence
    from infrastructure.repository.sqlite_sentence_repository import _compute_sentence_hash
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    with Session() as session:
        h = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        row = session.query(DbSentence).filter(DbSentence.input_hash == h).first()
        assert row is not None
        assert row.audio_path == "/tmp/audio.mp3"
        assert row.voice_name == "en-US-Wavenet-A"
        assert row.voice_model == "tts-v2"
        assert row.audio_set_at is not None
    print("test_set_audio_path_sentence passed")


def test_duplicate_save_raises():
    repo = SqliteSentenceRepository(_make_engine())
    sentence = _make_sentence()
    repo.save(sentence)
    try:
        repo.save(sentence)
        assert False, "Expected ValueError on duplicate save"
    except ValueError:
        pass
    print("test_duplicate_save_raises passed")


# ── Vocab repository tests ─────────────────────────────────────────────────


def test_vocab_save_and_find():
    repo = SqliteVocabRepository(_make_engine())
    repo.save("english", "hindi", "walk", "चलना")
    result = repo.find("english", "hindi", "walk")
    assert result == "चलना", f"Expected 'चलना' but got {result}"
    print("test_vocab_save_and_find passed")


def test_vocab_miss_returns_none():
    repo = SqliteVocabRepository(_make_engine())
    result = repo.find("english", "hindi", "walk")
    assert result is None, f"Expected None on miss but got {result}"
    print("test_vocab_miss_returns_none passed")


def test_vocab_set_audio_path():
    engine = _make_engine()
    repo = SqliteVocabRepository(engine)
    repo.save("english", "hindi", "walk", "चलना")
    repo.set_audio_path("english", "hindi", "walk", "/tmp/walk.mp3", "hi-IN-Standard-A", "tts-v1")
    from infrastructure.models.db_vocab import DbVocab
    from infrastructure.repository.sqlite_vocab_repository import _compute_vocab_hash
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    with Session() as session:
        h = _compute_vocab_hash("english", "hindi", "walk")
        row = session.query(DbVocab).filter(DbVocab.input_hash == h).first()
        assert row is not None
        assert row.audio_path == "/tmp/walk.mp3"
        assert row.voice_name == "hi-IN-Standard-A"
        assert row.voice_model == "tts-v1"
        assert row.audio_set_at is not None
    print("test_vocab_set_audio_path passed")


def test_vocab_duplicate_save_raises():
    repo = SqliteVocabRepository(_make_engine())
    repo.save("english", "hindi", "walk", "चलना")
    try:
        repo.save("english", "hindi", "walk", "चलना")
        assert False, "Expected ValueError on duplicate save"
    except ValueError:
        pass
    print("test_vocab_duplicate_save_raises passed")


if __name__ == "__main__":
    test_save_and_find_hit()
    test_cache_miss_returns_none()
    test_mark_rejected_cached()
    test_mark_valid_not_in_rejected()
    test_set_audio_path_sentence()
    test_duplicate_save_raises()
    test_vocab_save_and_find()
    test_vocab_miss_returns_none()
    test_vocab_set_audio_path()
    test_vocab_duplicate_save_raises()
    print("\nAll tests passed.")
