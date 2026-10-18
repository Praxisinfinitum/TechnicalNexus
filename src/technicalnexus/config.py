"""Validated configuration independent of the interface."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Settings:
    database_url: str
    language: str = "es"
    manuals_path: Path = ROOT / "ManualesDeImpresoras" / "DCP-T430W"

    def __post_init__(self):
        if make_url(self.database_url).get_backend_name() != "postgresql":
            raise ValueError("PostgreSQL is required")
        if self.language != "es":
            raise ValueError("Only the Spanish catalog is implemented")

    @classmethod
    def load(cls):
        load_dotenv(ROOT / ".env", override=False)
        value = os.environ.get("DATABASE_URL")
        if not value:
            raise ValueError("DATABASE_URL is required; see .env.example")
        path = Path(os.environ.get("MANUALS_PATH", "ManualesDeImpresoras/DCP-T430W"))
        return cls(value, os.environ.get("APP_LANGUAGE", "es"), path if path.is_absolute() else ROOT / path)
