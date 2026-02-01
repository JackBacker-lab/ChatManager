from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str


def load_config() -> Config:
    """Load bot configuration from a local .env file."""
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    load_dotenv(env_path)

    if token := getenv("BOT_TOKEN"):
        return Config(bot_token=token)
    else:
        raise RuntimeError("BOT_TOKEN is not set")
