from pathlib import Path

import genanki
from domain.deck_writer import DeckWriter
from domain.models.deck import Deck

_MODEL_ID = 1708392319  # stable arbitrary model ID for Janulus AI card type


class AnkiDeckWriter(DeckWriter):

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def _build_package(self, deck: Deck) -> tuple[genanki.Package, str]:
        deck_id = abs(hash(deck.name)) % (10**10)

        anki_model = genanki.Model(
            _MODEL_ID,
            "Janulus AI",
            fields=[
                {"name": "Primary"},
                {"name": "Foreign"},
                {"name": "Sound"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": '<div class="primary">{{Primary}}</div>',
                    "afmt": '{{FrontSide}}<hr id="answer"><div class="foreign">{{Foreign}}</div>\n{{#Sound}}<div class="sound-btn">{{Sound}}</div>{{/Sound}}',
                },
            ],
            css="""
.card {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #2c3e50;
  padding: 30px 20px;
}
.primary {
  font-size: 22px;
  font-weight: 500;
  line-height: 1.5;
  margin-bottom: 16px;
}
.foreign {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.5;
  margin-top: 16px;
}
hr#answer {
  border: none;
  border-top: 1px solid #d5d8dc;
  margin: 20px 0;
}
""",
        )

        anki_deck = genanki.Deck(deck_id, deck.name)

        media_files = [entry.audio_path for entry in deck.entries if entry.audio_path]

        for entry in deck.entries:
            sound_field = f"[sound:{Path(entry.audio_path).name}]" if entry.audio_path else ""

            note = genanki.Note(
                model=anki_model,
                fields=[entry.primary_text, entry.foreign_text, sound_field],
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
