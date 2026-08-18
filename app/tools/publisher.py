from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from app.memory.state_manager import (
    CuratedItem,
    CustomerProfile,
    NewsletterDraft,
    PublishNewsletterInput,
    ToolErrorResponse,
    ToolStatus,
)
from app.observability.tracer import tracer


def format_newsletter_markdown(
    customer_profile: Union[CustomerProfile, Dict[str, Any]],
    curated_items: Union[List[CuratedItem], List[Dict[str, Any]]],
    output_format: str = "markdown"
) -> Union[NewsletterDraft, ToolErrorResponse]:
    """Formats curated release notes into an executive newsletter document.
    
    Args:
        customer_profile: CustomerProfile instance or dictionary.
        curated_items: List of CuratedItem instances or dictionaries.
        output_format: Output format ('markdown' or 'html').
        
    Returns:
        NewsletterDraft containing title, metadata, item counts, and formatted content string, or ToolErrorResponse.
        
    Recovery Guidance:
        Provide customer_profile with at least 'name', and curated_items with at least one CuratedItem.
    """
    cust_name = getattr(customer_profile, "name", None) or (customer_profile.get("name") if isinstance(customer_profile, dict) else "Customer")
    with tracer.trace_span("format_newsletter_markdown", {"customer_name": cust_name, "format": output_format}):
        try:
            if isinstance(customer_profile, dict):
                profile = CustomerProfile(**customer_profile)
            else:
                profile = customer_profile

            items: List[CuratedItem] = []
            for c in (curated_items or []):
                if isinstance(c, dict):
                    items.append(CuratedItem(**c))
                else:
                    items.append(c)
        except ValidationError as e:
            tracer.warning("publisher_validation_error", f"Validation error: {str(e)}")
            return ToolErrorResponse(
                error_type="VALIDATION_ERROR",
                error_message=f"Could not format newsletter: {str(e)}",
                recovery_instructions="Provide valid customer_profile and non-empty curated_items list.",
                suggested_action="format_newsletter_markdown"
            )

        if not items:
            tracer.warning("publisher_empty_curated_items", "No curated items provided to publisher")
            return ToolErrorResponse(
                error_type="EMPTY_CURATED_ITEMS",
                error_message="Cannot generate newsletter without curated items.",
                recovery_instructions="Call score_and_rank_release_notes first before attempting to format newsletter.",
                suggested_action="score_and_rank_release_notes"
            )

        high_items = [i for i in items if i.relevance_score == "High"]
        med_items = [i for i in items if i.relevance_score == "Medium"]
        low_items = [i for i in items if i.relevance_score == "Low"]

        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
        title = f"Google Cloud & Gemini Enterprise Executive Update: {profile.name}"

        lines = [
            f"# {title}",
            f"**Prepared For:** {profile.name} ({profile.tier})",
            f"**Industry Vertical:** {profile.industry}",
            f"**Date:** {date_str} | **Curated By:** Google ADK Autonomous Agent",
            "",
            "---",
            "",
            "## 🎯 Strategic Summary & Tailored Context",
            f"This personalized briefing is curated specifically for **{profile.name}** based on your technology ecosystem:",
            f"- **Active Stack:** {', '.join(profile.tech_stack)}",
            f"- **Strategic Priorities:** {', '.join(profile.priorities)}",
            "",
            f"Out of **{len(items)}** recent platform updates evaluated, **{len(high_items)} critical high-impact announcements** require direct attention.",
            "",
            "---",
            ""
        ]

        if high_items:
            lines.append("## 🚨 High-Priority Platform Updates (Immediate Action Required)")
            lines.append("")
            for idx, c in enumerate(high_items, 1):
                item = c.item
                lines.extend([
                    f"### {idx}. {item.title} `[{item.category}]` `[{item.status_type}]`",
                    f"- **Published Date:** {item.published_date}",
                    f"- **Summary:** {item.summary}",
                    f"- **🎯 Why It Matters to {profile.name}:** {c.why_it_matters}",
                    f"- **📋 Recommended Next Action:** {c.recommended_action}",
                    f"- 🔗 [Official Documentation & Release Notes]({item.url})",
                    ""
                ])

        if med_items:
            lines.append("## 💡 Medium-Priority Updates (Sprint Planning & Architectural Awareness)")
            lines.append("")
            for idx, c in enumerate(med_items, 1):
                item = c.item
                lines.extend([
                    f"### {idx}. {item.title} `[{item.category}]`",
                    f"- **Summary:** {item.summary}",
                    f"- **Architectural Relevance:** {c.why_it_matters}",
                    f"- **Action:** {c.recommended_action}",
                    f"- 🔗 [Documentation]({item.url})",
                    ""
                ])

        if low_items:
            lines.append("## 📌 General Ecosystem & Platform Notes")
            lines.append("")
            for idx, c in enumerate(low_items, 1):
                item = c.item
                lines.extend([
                    f"- **{item.title}** ({item.category}): {item.summary} [Link]({item.url})"
                ])
            lines.append("")

        lines.extend([
            "---",
            "*Generated with Google Agent Development Kit (ADK), Gemini Enterprise Agent Platform, and OpenTelemetry Distributed Observability.*"
        ])

        full_content = "\n".join(lines)
        draft = NewsletterDraft(
            title=title,
            customer_name=profile.name,
            content=full_content,
            high_priority_count=len(high_items),
            total_items=len(items)
        )
        tracer.info("newsletter_published", f"Formatted newsletter draft for {profile.name}", length=len(full_content), high_priority=len(high_items))
        return draft
