import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.models.deck import Deck, build_deck_name
from domain.models.deck_entry import DeckEntry
from domain.models.grammar_options import SentenceType, Tense
from infrastructure.csv_deck_writer import CsvDeckWriter
from infrastructure.anki_deck_writer import AnkiDeckWriter


def _sample_deck() -> Deck:
    entries = [
        DeckEntry(
            primary_language_code="en",
            foreign_language_code="hi",
            primary_text="I eat an apple.",
            foreign_text="मैं एक सेब खाता हूँ।",
            audio_path=None,
            tags=["simple-present", "declarative"],
        ),
        DeckEntry(
            primary_language_code="en",
            foreign_language_code="hi",
            primary_text="She is reading a book.",
            foreign_text="वह एक किताब पढ़ रही है।",
            audio_path="she_reads.mp3",
            tags=["present-continuous", "declarative", "audio"],
        ),
        DeckEntry(
            primary_language_code="en",
            foreign_language_code="hi",
            primary_text="Did they go to the market?",
            foreign_text="क्या वे बाज़ार गए?",
            audio_path=None,
            tags=["simple-past", "interrogative"],
        ),
    ]
    return Deck(name="hindi_noaudio_simple-present_declarative", entries=entries)


def test_csv_writer():
    deck = _sample_deck()
    with tempfile.TemporaryDirectory() as tmpdir:
        writer = CsvDeckWriter(Path(tmpdir))
        result = writer.write(deck)

        output_path = Path(result)
        assert output_path.exists(), "CSV file was not created"
        assert output_path.name == f"{deck.name}.csv"

        with open(output_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        # header + 3 data rows
        assert len(rows) == 4, f"Expected 4 rows (1 header + 3 data), got {len(rows)}"

        header = rows[0]
        assert header == [
            "primary_language_code",
            "foreign_language_code",
            "primary_text",
            "foreign_text",
            "audio_path",
            "tags",
        ]

        # Check tag format: space-separated
        tags_col = header.index("tags")
        assert rows[1][tags_col] == "simple-present declarative"
        assert rows[2][tags_col] == "present-continuous declarative audio"
        assert rows[3][tags_col] == "simple-past interrogative"


def test_anki_writer():
    deck = _sample_deck()
    with tempfile.TemporaryDirectory() as tmpdir:
        writer = AnkiDeckWriter(Path(tmpdir))
        result = writer.write(deck)

        assert result == deck.name, f"Expected deck name '{deck.name}', got '{result}'"

        output_path = Path(tmpdir) / f"{deck.name}.apkg"
        assert output_path.exists(), ".apkg file was not created"


def test_build_deck_name():
    # Single tense and type
    assert (
        build_deck_name("Hindi", has_audio=True, tense=Tense.SIMPLE_PRESENT, sentence_type=SentenceType.DECLARATIVE)
        == "hindi_audio_simple-present_declarative"
    )

    # Multi-tense deck (tense=None → "mixed")
    assert (
        build_deck_name("Hindi", has_audio=True, tense=None, sentence_type=SentenceType.DECLARATIVE)
        == "hindi_audio_mixed_declarative"
    )

    # Fully mixed
    assert (
        build_deck_name("Hindi", has_audio=False, tense=None, sentence_type=None)
        == "hindi_noaudio_mixed_mixed"
    )

    # Spanish, past, interrogative, no audio
    assert (
        build_deck_name("Spanish", has_audio=False, tense=Tense.SIMPLE_PAST, sentence_type=SentenceType.INTERROGATIVE)
        == "spanish_noaudio_simple-past_interrogative"
    )

    # Underscore-in-value tenses get converted to hyphens
    assert (
        build_deck_name("French", has_audio=True, tense=Tense.PRESENT_PERFECT_CONTINUOUS, sentence_type=SentenceType.EXCLAMATORY)
        == "french_audio_present-perfect-continuous_exclamatory"
    )


if __name__ == "__main__":
    test_build_deck_name()
    print("test_build_deck_name passed")

    test_csv_writer()
    print("test_csv_writer passed")

    test_anki_writer()
    print("test_anki_writer passed")

    print("All tests passed.")
