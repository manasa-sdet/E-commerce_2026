import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
TEST_ENV = os.getenv("TEST_ENV", "qa")

# load_dotenv doesn't override vars that are already set, so the first file wins
# (and real env vars win over all of them)
for name in (f".env.{TEST_ENV}", ".env", ".env.example"):
    load_dotenv(ROOT_DIR / name, override=False)


def _required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            f"Set it in .env.{TEST_ENV} or in the process environment (see .env.example)."
        )
    return value


@dataclass(frozen=True)
class Settings:
    web_base_url: str
    api_base_url: str

    # properties so that UI-only runs don't need API credentials
    @property
    def api_email(self):
        return _required("RSA_API_EMAIL")

    @property
    def api_password(self):
        return _required("RSA_API_PASSWORD")


settings = Settings(
    web_base_url=_required("WEB_BASE_URL").rstrip("/"),
    api_base_url=_required("API_BASE_URL").rstrip("/"),
)
