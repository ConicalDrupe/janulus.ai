from sqlalchemy import Boolean, Column, Integer, String

from domain.models.generated_sentence import GeneratedSentence
from domain.models.grammar_options import (
    GrammaticalNumber,
    GrammarOptions,
    SentenceType,
    Tense,
)
from infrastructure.models.base import Base


class DbSentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True)
    input_hash = Column(String, unique=True, nullable=False, index=True)
    L1 = Column(String, nullable=False)
    L2 = Column(String, nullable=False)
    L1_text = Column(String, nullable=False)
    L2_text = Column(String, nullable=False)
    tense = Column(String, nullable=False)
    sentence_type = Column(String)
    grammatical_number = Column(String)
    include_preposition = Column(Boolean, nullable=False)
    include_possession = Column(Boolean, nullable=False)
    is_valid = Column(Boolean)
    audio_path = Column(String)
    voice_name = Column(String)
    voice_model = Column(String)
    created_at = Column(String, nullable=False)
    validated_at = Column(String)
    audio_set_at = Column(String)

    def to_domain(self) -> GeneratedSentence:
        grammar_options = GrammarOptions(
            tense=Tense(self.tense),
            sentence_type=SentenceType(self.sentence_type) if self.sentence_type else None,
            grammatical_number=GrammaticalNumber(self.grammatical_number) if self.grammatical_number else None,
            include_preposition=self.include_preposition,
            include_possession=self.include_possession,
        )
        return GeneratedSentence(
            L1=self.L1,
            L2=self.L2,
            L1_text=self.L1_text,
            L2_text=self.L2_text,
            grammar_options=grammar_options,
        )
