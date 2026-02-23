import os
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine, create_engine

_ADDON_DIR = Path(__file__).parent


@dataclass(frozen=True)
class InfraConfig:
    addon_dir: Path
    user_files_dir: Path
    db_path: Path
    audio_dir: Path
    google_project_id: str
    google_location: str
    elevenlabs_api_key: str


def load_infra_config() -> InfraConfig:
    addon_dir = _ADDON_DIR
    user_files_dir = addon_dir / "user_files"
    return InfraConfig(
        addon_dir=addon_dir,
        user_files_dir=user_files_dir,
        db_path=user_files_dir / "cache.db",
        audio_dir=user_files_dir / "audio",
        google_project_id=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        google_location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
    )


def make_engine(config: InfraConfig) -> Engine:
    config.user_files_dir.mkdir(parents=True, exist_ok=True)
    config.audio_dir.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{config.db_path}")
