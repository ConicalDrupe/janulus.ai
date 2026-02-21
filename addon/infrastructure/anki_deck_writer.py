from pathlib import Path

import genanki

from domain.deck_writer import DeckWriter
from domain.models.deck import Deck

_MODEL_ID = 1607392319  # stable arbitrary model ID for Basic card type


class AnkiDeckWriter(DeckWriter):

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def write(self, deck: Deck) -> str:
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

        for entry in deck.entries:
            if entry.audio_path:
                front = f"{entry.foreign_text} [sound:{entry.audio_path}]"
            else:
                front = entry.foreign_text

            note = genanki.Note(
                model=anki_model,
                fields=[front, entry.primary_text],
                tags=entry.tags,
            )
            anki_deck.add_note(note)

        output_path = self.output_dir / f"{deck.name}.apkg"
        genanki.Package(anki_deck).write_to_file(str(output_path))

        return deck.name
