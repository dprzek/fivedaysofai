import pytest
from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import rank_and_curate_release_notes
from app.tools.publisher import format_personalized_newsletter


def test_lookup_existing_customer():
    profile = lookup_customer_profile("FinTech Global Bank")
    assert profile["name"] == "FinTech Global Bank"
    assert "Financial Services" in profile["industry"]
    assert any("Spanner" in t for t in profile["tech_stack"])
    assert any("Security" in p or "Governance" in p for p in profile["priorities"])


def test_lookup_dynamic_customer():
    profile = lookup_customer_profile("Acme AI Labs")
    assert profile["name"] == "Acme Ai Labs"
    assert "Technology" in profile["industry"]
    assert len(profile["tech_stack"]) > 0


def test_register_and_update_customer():
    result = register_or_update_customer_profile(
        name="Custom Retail Corp",
        industry="Retail & E-commerce",
        tech_stack=["BigQuery", "Vertex AI", "Cloud Storage"],
        priorities=["Real-time inventory search", "Personalized recommendations"]
    )
    assert result["name"] == "Custom Retail Corp"
    assert result["industry"] == "Retail & E-commerce"
    
    # Retrieve again
    retrieved = lookup_customer_profile("Custom Retail Corp")
    assert retrieved["industry"] == "Retail & E-commerce"
    assert "BigQuery" in retrieved["tech_stack"]


def test_fetch_cloud_release_notes():
    notes = fetch_cloud_release_notes(limit=10)
    assert len(notes) >= 5
    first_note = notes[0]
    assert "title" in first_note
    assert "summary" in first_note
    assert "category" in first_note
    assert "url" in first_note
    assert "status_type" in first_note


def test_rank_and_curate_release_notes():
    profile = lookup_customer_profile("FinTech Global Bank")
    notes = fetch_cloud_release_notes(limit=10)
    curated = rank_and_curate_release_notes(profile, notes)
    
    assert len(curated) == len(notes)
    high_items = [c for c in curated if c["relevance_score"] == "High"]
    assert len(high_items) >= 1
    
    first_high = high_items[0]
    assert "why_it_matters" in first_high
    assert "recommended_action" in first_high
    assert "FinTech Global Bank" in first_high["why_it_matters"]


def test_format_personalized_newsletter():
    profile = lookup_customer_profile("MediaStream Studios")
    notes = fetch_cloud_release_notes(limit=10)
    curated = rank_and_curate_release_notes(profile, notes)
    
    newsletter = format_personalized_newsletter(profile, curated)
    
    assert "MediaStream Studios" in newsletter["title"]
    assert "## 📌 Executive Summary" in newsletter["content"]
    assert "## 🚀 High-Priority Updates" in newsletter["content"]
    assert "## 📋 Recommended Action Items" in newsletter["content"]
    assert newsletter["high_priority_count"] >= 1
