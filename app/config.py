import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "default-project")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_cloud_trace: bool = os.getenv("ENABLE_CLOUD_TRACE", "false").lower() == "true"
    release_notes_url: str = os.getenv(
        "RELEASE_NOTES_URL",
        "https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes",
    )


config = AppConfig()
