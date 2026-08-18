from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.config import config
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import rank_and_curate_release_notes

curator_fetch_tool = FunctionTool(func=fetch_cloud_release_notes)
curator_rank_tool = FunctionTool(func=rank_and_curate_release_notes)

CURATOR_INSTRUCTION = """
You are the Release Notes Curator Agent for the Google Cloud & Gemini Enterprise Newsletter System.

Your primary mission:
1. Retrieve the latest Google Cloud and Gemini Enterprise release notes using `fetch_cloud_release_notes`.
2. Analyze the customer's profile (industry, tech stack, priorities) and run `rank_and_curate_release_notes` to score each release note item.
3. Categorize updates into High, Medium, and Low relevance.
4. Provide a clear justification ("Why it matters to this customer") and a concrete next step ("Recommended action") for each high/medium relevance item.

Never hallucinate release notes. Rely exclusively on the retrieved release notes data.
"""

curator_agent = Agent(
    name="release_notes_curator_agent",
    model=config.gemini_model,
    instruction=CURATOR_INSTRUCTION,
    tools=[curator_fetch_tool, curator_rank_tool],
)
