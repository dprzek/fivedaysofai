from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import score_and_rank_release_notes
from app.tools.publisher import format_newsletter_markdown

# Backwards compatibility alias
rank_and_curate_release_notes = score_and_rank_release_notes

__all__ = [
    "lookup_customer_profile",
    "register_or_update_customer_profile",
    "fetch_cloud_release_notes",
    "score_and_rank_release_notes",
    "rank_and_curate_release_notes",
    "format_newsletter_markdown",
]
