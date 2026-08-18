from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    name: str
    industry: str = "Technology"
    tech_stack: List[str] = Field(default_factory=list)
    priorities: List[str] = Field(default_factory=list)
    tier: str = "Enterprise"
    notes: Optional[str] = None
    contact_email: Optional[str] = None


class ReleaseNoteItem(BaseModel):
    id: str
    date: str
    title: str
    summary: str
    category: str = "General"
    status_type: str = "GA"  # GA, Preview, Deprecation
    url: Optional[str] = None
    raw_content: Optional[str] = None


class CuratedItem(BaseModel):
    release_note: ReleaseNoteItem
    relevance_score: str  # High, Medium, Low
    rationale: str
    why_it_matters: str
    recommended_action: str


class NewsletterDraft(BaseModel):
    customer_name: str
    title: str
    executive_summary: str
    curated_items: List[CuratedItem] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    format: str = "markdown"


def create_initial_state() -> Dict[str, Any]:
    return {
        "customer_name": "",
        "customer_profile": None,
        "release_notes": [],
        "curated_items": [],
        "newsletter_draft": None,
        "conversation_turn": 0,
        "user_feedback": [],
    }
