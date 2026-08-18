from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.config import config
from app.tools.publisher import format_personalized_newsletter

synthesizer_format_tool = FunctionTool(func=format_personalized_newsletter)

SYNTHESIZER_INSTRUCTION = """
You are the Newsletter Synthesizer Agent for the Google Cloud & Gemini Enterprise Newsletter System.

Your primary mission:
1. Synthesize the curated and ranked release notes into an engaging, executive-level newsletter tailored for the customer.
2. Structure the newsletter logically:
   - Executive Summary (tailored to customer's business priorities)
   - High-Priority Updates (direct impact on tech stack & roadmap, with status badges GA/Preview)
   - Relevant Platform & Operational Updates
   - Concrete Action Items & Next Steps for the customer's engineering team
3. Utilize `format_personalized_newsletter` to produce consistent, publication-ready markdown output.
4. Maintain a clear, authoritative, yet approachable engineering tone.
"""

synthesizer_agent = Agent(
    name="newsletter_synthesizer_agent",
    model=config.gemini_model,
    instruction=SYNTHESIZER_INSTRUCTION,
    tools=[synthesizer_format_tool],
)
