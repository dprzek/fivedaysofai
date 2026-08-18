import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Cloud Project & Location
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "adk-dev-485808")
    LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Strategic Multi-Model Tiering:
    # Fast Model (low latency, high throughput) for extraction, profile lookup, and ranking
    FAST_MODEL: str = os.getenv("GEMINI_FAST_MODEL", "gemini-2.5-flash")
    # Deep Reasoning Model (high context, complex formatting, rigorous fact-checking) for synthesis and evaluation
    REASONING_MODEL: str = os.getenv("GEMINI_REASONING_MODEL", "gemini-1.5-pro")
    
    # Per-Agent Strategic Routing
    PROFILER_MODEL: str = os.getenv("PROFILER_MODEL", FAST_MODEL)
    CURATOR_MODEL: str = os.getenv("CURATOR_MODEL", FAST_MODEL)
    SYNTHESIZER_MODEL: str = os.getenv("SYNTHESIZER_MODEL", REASONING_MODEL)
    CRITIC_MODEL: str = os.getenv("CRITIC_MODEL", REASONING_MODEL)
    ORCHESTRATOR_MODEL: str = os.getenv("ORCHESTRATOR_MODEL", FAST_MODEL)
    
    # App Settings
    APP_NAME: str = "personalized-cloud-newsletter-agent"
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # Human-in-the-Loop (HITL) Policy
    ENABLE_HITL: bool = os.getenv("ENABLE_HITL", "true").lower() == "true"
    HITL_AUTO_APPROVE_SAFE: bool = os.getenv("HITL_AUTO_APPROVE_SAFE", "false").lower() == "true"
    
    # Secret Manager
    USE_SECRET_MANAGER: bool = os.getenv("USE_SECRET_MANAGER", "false").lower() == "true"

config = Config()
