from pathlib import Path

import genanki

from domain.deck_writer import DeckWriter
from domain.models.deck import Deck

_MODEL_ID = 1607392319  # stable arbitrary model ID for Basic card type


class AnkiDeckWriter(DeckWriter):

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def _build_package(self, deck: Deck) -> tuple[genanki.Package, str]:
        deck_id = abs(hash(deck.name)) % (10**10)

        anki_model = genanki.Model(
            _MODEL_ID,
            "Basic",
            fields=[
                {"name": "Front"},
                {"name": "Back"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}<hr id=answer>{{Back}}",
                },
            ],
        )

        anki_deck = genanki.Deck(deck_id, deck.name)

        media_files = [entry.audio_path for entry in deck.entries if entry.audio_path]

        for entry in deck.entries:
            if entry.audio_path:
                front = f"{entry.foreign_text} [sound:{Path(entry.audio_path).name}]"
            else:
                front = entry.foreign_text

            note = genanki.Note(
                model=anki_model,
                fields=[front, entry.primary_text],
                tags=entry.tags,
            )
            anki_deck.add_note(note)

        return genanki.Package(anki_deck, media_files=media_files), deck.name

    def write(self, deck: Deck) -> str:
        package, deck_name = self._build_package(deck)
        output_path = self.output_dir / f"{deck_name}.apkg"
        package.write_to_file(str(output_path))
        return deck_name

    def write_to_collection(self, deck: Deck) -> str:
        """Import directly into the open Anki collection. Only works inside Anki."""
        package, deck_name = self._build_package(deck)
        package.write_to_collection_from_addon()
        return deck_name
