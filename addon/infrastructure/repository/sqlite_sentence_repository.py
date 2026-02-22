import hashlib
from datetime import datetime, timezone

from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from domain.models.generated_sentence import GeneratedSentence
from domain.repository.sentence_repository import SentenceRepository
from infrastructure.models.base import Base
from infrastructure.models.db_sentence import DbSentence


def _compute_sentence_hash(L1: str, L2: str, L2_text: str) -> str:
    parts = [L1.strip().lower(), L2.strip().lower(), L2_text.strip()]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


class SqliteSentenceRepository(SentenceRepository):
    def __init__(self, engine: Engine) -> None:
        self._Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

    def save(self, sentence: GeneratedSentence) -> None:
        input_hash = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        go = sentence.grammar_options
        now = datetime.now(timezone.utc).isoformat()
        row = DbSentence(
            input_hash=input_hash,
            L1=sentence.L1,
            L2=sentence.L2,
            L1_text=sentence.L1_text,
            L2_text=sentence.L2_text,
            tense=go.tense.value,
            sentence_type=go.sentence_type.value if go.sentence_type else None,
            grammatical_number=go.grammatical_number.value if go.grammatical_number else None,
            include_preposition=go.include_preposition,
            include_possession=go.include_possession,
            is_valid=None,
            created_at=now,
        )
        with self._Session() as session:
            try:
                session.add(row)
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Sentence already cached: {input_hash}")

    def find(self, sentence: GeneratedSentence) -> tuple[GeneratedSentence, bool | None] | None:
        input_hash = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        with self._Session() as session:
            row = session.query(DbSentence).filter(DbSentence.input_hash == input_hash).first()
            if row is None:
                return None
            return (row.to_domain(), row.is_valid)

    def find_rejected(self) -> list[GeneratedSentence]:
        with self._Session() as session:
            rows = session.query(DbSentence).filter(DbSentence.is_valid == False).all()  # noqa: E712
            return [row.to_domain() for row in rows]

    def mark_valid(self, sentence: GeneratedSentence) -> None:
        input_hash = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        now = datetime.now(timezone.utc).isoformat()
        with self._Session() as session:
            row = session.query(DbSentence).filter(DbSentence.input_hash == input_hash).first()
            if row is not None:
                row.is_valid = True
                row.validated_at = now
                session.commit()

    def mark_rejected(self, sentence: GeneratedSentence) -> None:
        input_hash = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        now = datetime.now(timezone.utc).isoformat()
        with self._Session() as session:
            row = session.query(DbSentence).filter(DbSentence.input_hash == input_hash).first()
            if row is not None:
                row.is_valid = False
                row.validated_at = now
                session.commit()

    def set_audio_path(
        self,
        sentence: GeneratedSentence,
        audio_path: str,
        voice_name: str,
        voice_model: str,
    ) -> None:
        input_hash = _compute_sentence_hash(sentence.L1, sentence.L2, sentence.L2_text)
        now = datetime.now(timezone.utc).isoformat()
        with self._Session() as session:
            row = session.query(DbSentence).filter(DbSentence.input_hash == input_hash).first()
            if row is not None:
                row.audio_path = audio_path
                row.voice_name = voice_name
                row.voice_model = voice_model
                row.audio_set_at = now
                session.commit()
