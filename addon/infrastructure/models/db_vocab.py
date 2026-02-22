from sqlalchemy import Column, Integer, String

from infrastructure.models.base import Base


class DbVocab(Base):
    __tablename__ = "vocabs"

    id = Column(Integer, primary_key=True)
    input_hash = Column(String, unique=True, nullable=False, index=True)
    L1 = Column(String, nullable=False)
    L2 = Column(String, nullable=False)
    L1_text = Column(String, nullable=False)
    L2_text = Column(String, nullable=False)
    audio_path = Column(String)
    voice_name = Column(String)
    voice_model = Column(String)
    created_at = Column(String, nullable=False)
    audio_set_at = Column(String)
