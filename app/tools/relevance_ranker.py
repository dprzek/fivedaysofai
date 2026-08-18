from typing import Any, Dict, List, Union
from pydantic import ValidationError

from app.memory.state_manager import (
    CuratedItem,
    CuratedReleaseNotesResponse,
    CustomerProfile,
    ReleaseNoteItem,
    ToolErrorResponse,
    ToolStatus,
)
from app.observability.tracer import tracer


def score_and_rank_release_notes(
    customer_profile: Union[CustomerProfile, Dict[str, Any]],
    release_notes: Union[List[ReleaseNoteItem], List[Dict[str, Any]]]
) -> Union[CuratedReleaseNotesResponse, ToolErrorResponse]:
    """Evaluates release notes against a customer's tech stack and priorities, ranking them by architectural relevance.
    
    Args:
        customer_profile: CustomerProfile object or dict with 'name', 'tech_stack', and 'priorities'.
        release_notes: List of ReleaseNoteItem objects or dicts.
        
    Returns:
        CuratedReleaseNotesResponse with ranked curated items, or ToolErrorResponse with recovery steps.
        
    Recovery Guidance:
        If profile or release notes list is empty or malformed, provide at least one valid customer tech stack and non-empty release notes list.
    """
    cust_name = getattr(customer_profile, "name", None) or (customer_profile.get("name") if isinstance(customer_profile, dict) else "Unknown")
    with tracer.trace_span("score_and_rank_release_notes", {"customer_name": cust_name}):
        try:
            if isinstance(customer_profile, dict):
                profile = CustomerProfile(**customer_profile)
            else:
                profile = customer_profile
                
            items: List[ReleaseNoteItem] = []
            for r in (release_notes or []):
                if isinstance(r, dict):
                    items.append(ReleaseNoteItem(**r))
                else:
                    items.append(r)
        except ValidationError as e:
            tracer.warning("relevance_ranker_validation_error", f"Validation error: {str(e)}")
            return ToolErrorResponse(
                error_type="VALIDATION_ERROR",
                error_message=f"Could not parse profile or release notes: {str(e)}",
                recovery_instructions="Provide customer_profile as a valid CustomerProfile or dict with 'name', 'tech_stack', and 'priorities', and release_notes as a non-empty list.",
                suggested_action="score_and_rank_release_notes"
            )
            
        if not items:
            tracer.warning("relevance_ranker_empty_items", "No release notes provided for ranking")
            return ToolErrorResponse(
                error_type="EMPTY_RELEASE_NOTES_LIST",
                error_message="No release note items were passed to the ranker.",
                recovery_instructions="Call fetch_cloud_release_notes first to retrieve release notes before scoring.",
                suggested_action="fetch_cloud_release_notes"
            )

        curated_results: List[CuratedItem] = []
        tech_stack_keywords = [kw.lower() for kw in profile.tech_stack]
        priority_keywords = [kw.lower() for kw in profile.priorities]
        industry_keywords = profile.industry.lower().split()

        for item in items:
            searchable_text = f"{item.title} {item.summary} {item.category}".lower()
            score = 25  # Base score

            matched_tech = [t for t in tech_stack_keywords if any(w in searchable_text for w in t.split() if len(w) > 3)]
            if matched_tech:
                score += 35

            matched_priorities = [p for p in priority_keywords if any(w in searchable_text for w in p.split() if len(w) > 3)]
            if matched_priorities:
                score += 25

            if any(ind in searchable_text for ind in industry_keywords if len(ind) > 3):
                score += 15

            score = min(100, score)

            if score >= 65:
                rel_level = "High"
                why = f"Directly impacts {profile.name}'s stack ({', '.join(matched_tech or profile.tech_stack[:2])}) and aligns with strategic priorities ({', '.join(matched_priorities or profile.priorities[:1])})."
                rec_action = f"Prioritize architectural review with the cloud engineering team to plan evaluation and migration."
            elif score >= 45:
                rel_level = "Medium"
                why = f"Relevant to general cloud modernization and {profile.industry} operational best practices."
                rec_action = f"Review technical documentation and assess applicability for upcoming quarterly sprints."
            else:
                rel_level = "Low"
                why = f"Broader Google Cloud platform update with informational value for architecture teams."
                rec_action = f"Archive for informational awareness."

            curated_results.append(CuratedItem(
                item=item,
                relevance_score=rel_level,
                numerical_score=score,
                why_it_matters=why,
                recommended_action=rec_action
            ))

        curated_results.sort(key=lambda x: x.numerical_score, reverse=True)
        high_priority = [c for c in curated_results if c.relevance_score == "High"]
        
        response = CuratedReleaseNotesResponse(
            customer_name=profile.name,
            total_analyzed=len(items),
            curated_items=curated_results,
            high_priority_count=len(high_priority)
        )
        tracer.info("relevance_ranking_completed", f"Ranked {len(items)} items for {profile.name}. High priority: {len(high_priority)}", count=len(items), high_priority_count=len(high_priority))
        return response
