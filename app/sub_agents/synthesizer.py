from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.config import config
from app.tools.publisher import format_newsletter_markdown

SYNTHESIZER_INSTRUCTIONS = """You are the specialized Newsletter Synthesizer Agent.
Your responsibility is to take curated release note items and transform them into an executive-ready, highly polished markdown briefing.

Highlight:
1. Executive strategic context customized to the customer's active tech stack and priorities.
2. High-impact immediate action items with clear 'Why It Matters' and 'Recommended Next Action'.
3. Medium-priority sprint planning opportunities.
4. General platform ecosystem updates.
"""

synthesizer_agent = Agent(
    name="newsletter_synthesizer_agent",
    model=config.SYNTHESIZER_MODEL,
    description="Synthesizes curated release notes into formatted executive newsletter briefings.",
    instruction=SYNTHESIZER_INSTRUCTIONS,
    tools=[
        FunctionTool(format_newsletter_markdown),
    ]
)
