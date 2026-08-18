from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.config import config
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import score_and_rank_release_notes

CURATOR_INSTRUCTIONS = """You are the specialized Release Notes Curator Agent.
Your responsibility is to fetch the latest Google Cloud and Gemini Enterprise release notes and evaluate their architectural relevance against the customer's technology profile.

Score and rank each release note (High, Medium, Low) and articulate specific 'why_it_matters' architectural impact.
"""

curator_agent = Agent(
    name="release_notes_curator_agent",
    model=config.CURATOR_MODEL,
    description="Fetches release notes and executes architectural relevance scoring for customer profiles.",
    instruction=CURATOR_INSTRUCTIONS,
    tools=[
        FunctionTool(fetch_cloud_release_notes),
        FunctionTool(score_and_rank_release_notes),
    ]
)
