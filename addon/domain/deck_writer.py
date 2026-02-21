from abc import ABC, abstractmethod

from domain.models.deck import Deck


class DeckWriter(ABC):

    @abstractmethod
    def write(self, deck: Deck) -> str:
        """
        Persist the deck and return an identifier:
        - CsvDeckWriter: returns the file path written to
        - AnkiDeckWriter: returns the deck name (genanki deck name string)
        """
        pass
