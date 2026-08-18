from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class ToolErrorResponse(BaseModel):
    """Structured error payload providing guided recovery instructions to LLMs."""
    status: ToolStatus = ToolStatus.ERROR
    error_type: str = Field(..., description="High-level category of error encountered")
    error_message: str = Field(..., description="Human-readable description of the failure")
    recovery_instructions: str = Field(..., description="Explicit step-by-step guidance for the LLM to fix parameters and retry")
    suggested_action: Optional[str] = Field(None, description="Suggested next tool call or parameter value")
    valid_options: Optional[List[str]] = Field(None, description="List of valid alternative values or categories")


class LookupCustomerInput(BaseModel):
    """Input parameters for looking up a customer in the CRM."""
    customer_name: str = Field(..., min_length=2, description="Exact or approximate name of the customer organization to look up.")


class RegisterCustomerInput(BaseModel):
    """Input parameters for registering or updating a customer profile in the CRM."""
    name: str = Field(..., min_length=2, description="Official name of the customer enterprise organization.")
    industry: str = Field(default="Technology & Cloud Computing", description="Primary industry vertical (e.g. Financial Services, Healthcare, Retail).")
    tech_stack: List[str] = Field(default_factory=lambda: ["Google Cloud Platform"], description="List of Google Cloud and partner technologies used.")
    priorities: List[str] = Field(default_factory=lambda: ["Cloud Modernization", "Security"], description="Top architectural, strategic, or business priorities.")
    tier: str = Field(default="Standard Enterprise", description="Customer support and account tier (e.g. Enterprise Tier 1, Enterprise Growth).")
    contact_email: Optional[str] = Field(None, description="Primary technical contact or distribution list email.")
    notes: Optional[str] = Field(None, description="Additional context or architectural considerations.")


class ReleaseNotesQueryInput(BaseModel):
    """Input parameters for fetching release notes."""
    url: Optional[str] = Field(default=None, description="Optional custom release notes URL.")
    category: Optional[str] = Field(default=None, description="Filter category: 'Gemini Enterprise', 'Google Cloud', 'Compute', 'Data', 'Security', etc.")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of release note items to retrieve.")


class CustomerProfile(BaseModel):
    """Represents a customer's organization profile, tech stack, and strategic priorities."""
    name: str = Field(..., description="Name of the customer enterprise organization.")
    industry: str = Field(default="Technology & Cloud Computing", description="Primary industry vertical.")
    tech_stack: List[str] = Field(default_factory=list, description="Google Cloud and partner services used.")
    priorities: List[str] = Field(default_factory=list, description="Top architectural and business priorities.")
    tier: str = Field(default="Standard Enterprise", description="Customer tier: Enterprise Tier 1, Enterprise Growth, Standard Enterprise.")
    contact_email: Optional[str] = Field(default=None, description="Primary technical contact email.")
    notes: Optional[str] = Field(default=None, description="Special instructions or compliance constraints.")


class ReleaseNoteItem(BaseModel):
    """Individual Google Cloud / Gemini Enterprise release note item."""
    id: str = Field(..., description="Unique hash or ID of the release item.")
    title: str = Field(..., description="Headline of the release update.")
    summary: str = Field(..., description="Detailed description of features and capabilities.")
    category: str = Field(default="Google Cloud", description="Category tag (e.g. Gemini Enterprise, AI/ML, Compute, Data).")
    url: str = Field(default="https://cloud.google.com/release-notes", description="Link to documentation.")
    published_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"), description="Date of release.")
    date: Optional[str] = Field(default=None, description="Alias for published_date.")
    status_type: str = Field(default="GA", description="Release status: GA, Preview, Deprecated, New Feature.")


class CurateReleaseNotesInput(BaseModel):
    """Input schema for ranking release notes."""
    customer_profile: CustomerProfile = Field(..., description="Target customer profile to evaluate against.")
    release_notes: List[ReleaseNoteItem] = Field(..., description="List of release note items to score and rank.")


class CuratedItem(BaseModel):
    """A release note item enriched with relevance scoring and customized customer impact."""
    item: Optional[ReleaseNoteItem] = Field(default=None, description="Original release note item.")
    release_note: Optional[ReleaseNoteItem] = Field(default=None, description="Alias for item.")
    relevance_score: str = Field(default="Medium", description="'High', 'Medium', or 'Low'")
    numerical_score: int = Field(default=50, description="Relevance score between 0 and 100")
    rationale: Optional[str] = Field(default=None, description="Ranking rationale.")
    why_it_matters: str = Field(default="", description="Tailored architectural analysis of why this update matters to the specific customer.")
    recommended_action: str = Field(default="", description="Actionable next step for the customer's engineering or platform team.")

    def model_post_init(self, __context: Any) -> None:
        if self.item is None and self.release_note is not None:
            self.item = self.release_note
        elif self.release_note is None and self.item is not None:
            self.release_note = self.item


class CuratedReleaseNotesResponse(BaseModel):
    """Output schema from relevance ranking."""
    status: ToolStatus = ToolStatus.SUCCESS
    customer_name: str
    total_analyzed: int
    curated_items: List[CuratedItem]
    high_priority_count: int


class PublishNewsletterInput(BaseModel):
    """Input parameters for generating newsletter output."""
    customer_profile: CustomerProfile = Field(..., description="Customer profile metadata.")
    curated_items: List[CuratedItem] = Field(..., description="Curated and ranked release notes.")
    output_format: str = Field(default="markdown", description="Output format: 'markdown' or 'html'.")


class NewsletterDraft(BaseModel):
    """Formatted executive newsletter draft."""
    status: ToolStatus = ToolStatus.SUCCESS
    title: str = Field(default="Personalized Cloud Briefing", description="Newsletter edition title.")
    customer_name: str = Field(..., description="Customer name.")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content: str = Field(default="", description="Full executive newsletter text in formatted Markdown/HTML.")
    executive_summary: Optional[str] = Field(default=None, description="Executive summary text.")
    curated_items: List[CuratedItem] = Field(default_factory=list, description="Curated items included.")
    action_items: List[str] = Field(default_factory=list, description="Key action items.")
    high_priority_count: int = Field(default=0)
    total_items: int = Field(default=0)



class AgentSessionState(BaseModel):
    """Root session state container for agent turns."""
    customer_name: Optional[str] = None
    customer_profile: Optional[CustomerProfile] = None
    raw_release_notes: List[ReleaseNoteItem] = Field(default_factory=list)
    curated_items: List[CuratedItem] = Field(default_factory=list)
    current_draft: Optional[NewsletterDraft] = None
    evaluation_feedback: Optional[str] = None
    is_verified: bool = False
    turn_count: int = 0
    history_summary: Optional[str] = None


def create_initial_state() -> Dict[str, Any]:
    """Factory creating a clean initial state dictionary compatible with session callbacks."""
    return {
        "customer_name": "",
        "customer_profile": None,
        "release_notes": [],
        "curated_items": [],
        "newsletter_draft": None,
        "conversation_turn": 0,
        "user_feedback": [],
    }

