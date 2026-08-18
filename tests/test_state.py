import pytest
from unittest.mock import MagicMock
from app.memory.state_manager import (
    CustomerProfile,
    ReleaseNoteItem,
    CuratedItem,
    NewsletterDraft,
    create_initial_state
)
from app.callbacks import initialize_newsletter_state, trace_agent_execution


def test_pydantic_schemas():
    profile = CustomerProfile(
        name="Test Corp",
        industry="Technology",
        tech_stack=["GKE", "BigQuery"],
        priorities=["Cost optimization"],
        tier="Enterprise",
        notes="High security",
        contact_email="test@testcorp.com"
    )
    assert profile.name == "Test Corp"
    assert len(profile.tech_stack) == 2
    
    rn = ReleaseNoteItem(
        id="rn-test-01",
        date="2026-08-01",
        title="Gemini 2.5 Flash GA",
        summary="Faster inference",
        category="Vertex AI",
        status_type="GA",
        url="https://cloud.google.com/vertex-ai/docs/release-notes"
    )
    assert rn.status_type == "GA"
    
    curated = CuratedItem(
        release_note=rn,
        relevance_score="High",
        rationale="Matches stack",
        why_it_matters="Saves cost",
        recommended_action="Test in sandbox"
    )
    assert curated.relevance_score == "High"
    
    draft = NewsletterDraft(
        customer_name="Test Corp",
        title="Digest for Test Corp",
        executive_summary="Executive summary for Test Corp",
        curated_items=[curated],
        action_items=["Review GKE changes"]
    )
    assert draft.customer_name == "Test Corp"
    assert draft.executive_summary == "Executive summary for Test Corp"


def test_initial_state_factory():
    state = create_initial_state()
    assert state["customer_name"] == ""
    assert state["conversation_turn"] == 0
    assert state["release_notes"] == []
    assert state["curated_items"] == []


@pytest.mark.asyncio
async def test_session_state_callback():
    mock_context = MagicMock()
    mock_context.state = {}
    
    await initialize_newsletter_state(mock_context)
    
    assert mock_context.state["customer_name"] == ""
    assert mock_context.state["conversation_turn"] == 1
    assert mock_context.state["release_notes"] == []
    assert mock_context.state["curated_items"] == []
    
    # Second turn increments turn
    await initialize_newsletter_state(mock_context)
    assert mock_context.state["conversation_turn"] == 2
    
    # After turn callback does not raise
    await trace_agent_execution(mock_context)
