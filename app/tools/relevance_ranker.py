from typing import Any, Dict, List
from app.observability.tracer import tracer


def rank_and_curate_release_notes(
    customer_profile: Dict[str, Any],
    release_notes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Analyzes and ranks release notes based on relevance to customer tech stack and priorities.
    
    Args:
        customer_profile: Customer metadata including industry, tech stack, and priorities.
        release_notes: List of raw or parsed release note entries.
        
    Returns:
        A list of curated release note items with relevance score, impact rationale, and recommended action.
    """
    with tracer.trace_span("rank_and_curate_release_notes", {"customer": customer_profile.get("name")}):
        customer_name = customer_profile.get("name", "Customer")
        tech_stack = [t.lower() for t in customer_profile.get("tech_stack", [])]
        priorities = [p.lower() for p in customer_profile.get("priorities", [])]
        industry = customer_profile.get("industry", "").lower()
        
        curated_results = []
        
        for rn in release_notes:
            title = rn.get("title", "")
            summary = rn.get("summary", "")
            category = rn.get("category", "")
            combined_text = f"{title} {summary} {category}".lower()
            
            score_points = 0
            reasons = []
            
            # Check match against customer priorities
            for priority in priorities:
                words = priority.split()
                if any(w in combined_text for w in words if len(w) > 3):
                    score_points += 3
                    reasons.append(f"Aligns with strategic priority: '{priority}'")
            
            # Check match against tech stack
            for tech in tech_stack:
                words = tech.split()
                if any(w in combined_text for w in words if len(w) > 3):
                    score_points += 2
                    reasons.append(f"Impacts current infrastructure component: '{tech}'")
            
            # Industry-specific relevance heuristics
            if "financial" in industry or "banking" in industry:
                if any(term in combined_text for term in ["governance", "security", "metric", "allow", "deny", "policy", "monitoring"]):
                    score_points += 3
                    reasons.append("High regulatory and audit compliance relevance for Financial Services")
            elif "media" in industry or "entertainment" in industry:
                if any(term in combined_text for term in ["video", "multimodal", "claude", "flash", "model", "throughput"]):
                    score_points += 3
                    reasons.append("Directly accelerates digital media and video AI processing workflows")
            elif "developer" in industry or "saas" in industry:
                if any(term in combined_text for term in ["cli", "sandbox", "codemender", "tools", "ci/cd"]):
                    score_points += 3
                    reasons.append("Enhances developer environment security and agent execution")
            
            # Determine tier
            if score_points >= 4:
                relevance = "High"
                why_it_matters = (
                    f"Directly addresses {customer_name}'s core focus on {', '.join(customer_profile.get('priorities', [])[:2])}. "
                    f"{reasons[0] if reasons else 'High strategic fit.'}"
                )
                recommended_action = f"Schedule technical review with {customer_name}'s cloud architecture team to pilot in non-prod."
            elif score_points >= 2:
                relevance = "Medium"
                why_it_matters = f"Provides operational or cost optimization value. {reasons[0] if reasons else 'Moderate interest.'}"
                recommended_action = "Review release documentation and assess integration timelines for Q3/Q4."
            else:
                relevance = "Low"
                why_it_matters = "General platform enhancement with minimal immediate impact on existing architecture."
                recommended_action = "Informational only; no immediate architectural action required."
                
            curated_results.append({
                "release_note": rn,
                "relevance_score": relevance,
                "rationale": "; ".join(reasons) if reasons else "General platform capability",
                "why_it_matters": why_it_matters,
                "recommended_action": recommended_action,
                "score_points": score_points
            })
            
        # Sort descending by relevance score points
        curated_results.sort(key=lambda x: x["score_points"], reverse=True)
        tracer.info(
            "ranking_complete",
            f"Curated {len(curated_results)} release notes for {customer_name}",
            high_count=sum(1 for c in curated_results if c["relevance_score"] == "High"),
            medium_count=sum(1 for c in curated_results if c["relevance_score"] == "Medium")
        )
        return curated_results
