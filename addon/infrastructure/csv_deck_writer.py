import csv
from pathlib import Path

from domain.deck_writer import DeckWriter
from domain.models.deck import Deck


class CsvDeckWriter(DeckWriter):
    # Columns: primary_language_code, foreign_language_code,
    #          primary_text, foreign_text, audio_path, tags

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def write(self, deck: Deck) -> str:
        output_path = self.output_dir / f"{deck.name}.csv"
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "primary_language_code",
                "foreign_language_code",
                "primary_text",
                "foreign_text",
                "audio_path",
                "tags",
            ])
            for entry in deck.entries:
                writer.writerow([
                    entry.primary_language_code,
                    entry.foreign_language_code,
                    entry.primary_text,
                    entry.foreign_text,
                    entry.audio_path,
                    " ".join(entry.tags),
                ])
        return str(output_path)
