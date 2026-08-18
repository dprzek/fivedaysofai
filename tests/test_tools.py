import pytest
from app.memory.state_manager import (
    CustomerProfile,
    ReleaseNoteItem,
    CuratedItem,
    ToolStatus,
    ToolErrorResponse,
)
from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import score_and_rank_release_notes
from app.tools.publisher import format_newsletter_markdown


def test_lookup_customer_profile_known():
    profile = lookup_customer_profile("FinTech Global Bank")
    assert isinstance(profile, CustomerProfile)
    assert profile.name == "FinTech Global Bank"
    assert "Cloud Spanner" in profile.tech_stack


def test_lookup_customer_profile_fuzzy():
    profile = lookup_customer_profile("MediaStream")
    assert isinstance(profile, CustomerProfile)
    assert "MediaStream" in profile.name
    assert "Vertex AI" in profile.tech_stack


def test_lookup_customer_profile_dynamic():
    profile = lookup_customer_profile("Acme Corp Innovations")
    assert isinstance(profile, CustomerProfile)
    assert profile.name == "Acme Corp Innovations"
    assert len(profile.tech_stack) > 0


def test_register_customer_profile():
    new_profile = register_or_update_customer_profile(
        name="Healthcare Dynamics",
        industry="Healthcare & Life Sciences",
        tech_stack=["Cloud Healthcare API", "BigQuery", "Vertex AI"],
        priorities=["HIPAA Compliance", "Clinical Note Summarization"],
        tier="Enterprise Tier 1"
    )
    assert isinstance(new_profile, CustomerProfile)
    assert new_profile.name == "Healthcare Dynamics"

    # Verify retrieval
    retrieved = lookup_customer_profile("Healthcare Dynamics")
    assert isinstance(retrieved, CustomerProfile)
    assert "Cloud Healthcare API" in retrieved.tech_stack


def test_fetch_cloud_release_notes_fallback():
    notes = fetch_cloud_release_notes(limit=5)
    assert isinstance(notes, list)
    assert len(notes) >= 3
    assert all(isinstance(n, ReleaseNoteItem) for n in notes)


def test_score_and_rank_release_notes():
    profile = CustomerProfile(
        name="FinTech Global Bank",
        industry="Financial Services & Banking",
        tech_stack=["Cloud Spanner", "Cloud Armor", "BigQuery"],
        priorities=["Security & Governance", "Audit Compliance"]
    )
    notes = fetch_cloud_release_notes(limit=10)
    response = score_and_rank_release_notes(profile, notes)
    
    assert response.status == ToolStatus.SUCCESS
    assert response.total_analyzed == len(notes)
    assert len(response.curated_items) == len(notes)
    # Check that high score items are sorted first
    assert response.curated_items[0].numerical_score >= response.curated_items[-1].numerical_score


def test_format_newsletter_markdown():
    profile = CustomerProfile(
        name="Retail Pulse",
        industry="E-Commerce & Retail",
        tech_stack=["Gemini Enterprise Agent Platform"],
        priorities=["Agent Observability"]
    )
    notes = fetch_cloud_release_notes(limit=5)
    ranked = score_and_rank_release_notes(profile, notes)
    newsletter = format_newsletter_markdown(profile, ranked.curated_items)
    
    assert newsletter.status == ToolStatus.SUCCESS
    assert "Retail Pulse" in newsletter.title
    assert "Strategic Summary" in newsletter.content
    assert len(newsletter.content) > 200


def test_guided_error_handling_empty_items():
    profile = CustomerProfile(name="Empty Test", tech_stack=[], priorities=[])
    res = score_and_rank_release_notes(profile, [])
    assert isinstance(res, ToolErrorResponse)
    assert res.error_type == "EMPTY_RELEASE_NOTES_LIST"
    assert "Call fetch_cloud_release_notes first" in res.recovery_instructions
