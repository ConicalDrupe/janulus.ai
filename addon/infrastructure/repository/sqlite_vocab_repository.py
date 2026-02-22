import hashlib
from datetime import datetime, timezone

from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from domain.repository.vocab_repository import VocabRepository
from infrastructure.models.base import Base
from infrastructure.models.db_vocab import DbVocab


def _compute_vocab_hash(L1: str, L2: str, L1_text: str) -> str:
    parts = [L1.strip().lower(), L2.strip().lower(), L1_text.strip().lower()]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


class SqliteVocabRepository(VocabRepository):
    def __init__(self, engine: Engine) -> None:
        self._Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)

    def save(self, L1: str, L2: str, L1_text: str, L2_text: str) -> None:
        input_hash = _compute_vocab_hash(L1, L2, L1_text)
        now = datetime.now(timezone.utc).isoformat()
        row = DbVocab(
            input_hash=input_hash,
            L1=L1,
            L2=L2,
            L1_text=L1_text,
            L2_text=L2_text,
            created_at=now,
        )
        with self._Session() as session:
            try:
                session.add(row)
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Vocab already cached: {input_hash}")

    def find(self, L1: str, L2: str, L1_text: str) -> str | None:
        input_hash = _compute_vocab_hash(L1, L2, L1_text)
        with self._Session() as session:
            row = session.query(DbVocab).filter(DbVocab.input_hash == input_hash).first()
            if row is None:
                return None
            return row.L2_text

    def set_audio_path(
        self,
        L1: str,
        L2: str,
        L1_text: str,
        audio_path: str,
        voice_name: str,
        voice_model: str,
    ) -> None:
        input_hash = _compute_vocab_hash(L1, L2, L1_text)
        now = datetime.now(timezone.utc).isoformat()
        with self._Session() as session:
            row = session.query(DbVocab).filter(DbVocab.input_hash == input_hash).first()
            if row is not None:
                row.audio_path = audio_path
                row.voice_name = voice_name
                row.voice_model = voice_model
                row.audio_set_at = now
                session.commit()
