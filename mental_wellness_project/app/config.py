import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

load_dotenv()


@dataclass
class Settings:
    """
    Centralized application settings so the same configuration is shared by
    every module (models, routes, tasks, etc.).
    """

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "replace_with_openai_api_key")
    huggingface_api_key: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    db_path: Path = field(default=BASE_DIR / "mental_wellness.db")
    storage_dir: Path = field(default=STORAGE_DIR)

    # Application level thresholds / keywords
    harmful_keywords: tuple = (
        "self-harm",
        "suicide",
        "kill myself",
        "worthless",
        "panic",
        "violence",
        "abuse",
        "trigger warning",
    )

    calm_keywords: tuple = (
        "breathe",
        "calm",
        "relax",
        "gratitude",
        "journal",
    )

    activity_map: dict = field(
        default_factory=lambda: {
            "sad": [
                "Take a short mindful walk outside.",
                "Listen to your favorite upbeat playlist.",
                "Call a trusted friend and share how you feel.",
            ],
            "anxious": [
                "Try the 4-7-8 breathing technique for two minutes.",
                "Write down three things you can control right now.",
                "Stretch your shoulders, neck, and jaw to release tension.",
            ],
            "stressed": [
                "Drink a glass of water slowly and focus on the taste.",
                "Tackle a quick win task to regain momentum.",
                "Step away from the screen for five minutes of silence.",
            ],
            "neutral": [
                "Schedule something fun for later today.",
                "Send a kind message to someone you appreciate.",
            ],
        }
    )


settings = Settings()
