from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.callbacks import initialize_newsletter_state, trace_agent_execution
from app.config import config
from app.sub_agents.critic import critic_agent
from app.sub_agents.curator import curator_agent
from app.sub_agents.profiler import profiler_agent
from app.sub_agents.synthesizer import synthesizer_agent
from app.tools.customer_crm import (
    lookup_customer_profile,
    register_or_update_customer_profile,
)
from app.tools.publisher import format_personalized_newsletter
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import rank_and_curate_release_notes

# Root tools for direct orchestration and tool trajectories
crm_lookup_tool = FunctionTool(func=lookup_customer_profile)
crm_update_tool = FunctionTool(func=register_or_update_customer_profile)
fetch_rn_tool = FunctionTool(func=fetch_cloud_release_notes)
rank_rn_tool = FunctionTool(func=rank_and_curate_release_notes)
format_newsletter_tool = FunctionTool(func=format_personalized_newsletter)

ROOT_ORCHESTRATOR_INSTRUCTION = """
You are the Lead Google Cloud & Gemini Enterprise Newsletter Orchestration Agent.
Your mission is to craft highly personalized, executive-ready technical newsletters for Google Cloud enterprise customers based on official Google Cloud and Gemini Enterprise release notes.

Follow this standard multi-step workflow:

### Step 1: Customer Identification & Profiling
- In the initial turn, identify the customer name from user input. If missing or ambiguous, ask the user: "Which customer would you like to generate the release notes newsletter for?"
- When customer name is known, invoke `lookup_customer_profile` to retrieve their industry, current cloud tech stack, and strategic priorities.
- Summarize the identified customer profile to the user and highlight their focus areas.

### Step 2: Release Notes Retrieval & Curation
- Call `fetch_cloud_release_notes` to fetch recent platform announcements.
- Call `rank_and_curate_release_notes` passing the customer profile and fetched release notes.
- Categorize updates into High, Medium, and Low relevance, formulating concrete "Why it matters to [Customer]" insights and recommended actions.

### Step 3: Synthesis & Publication
- Call `format_personalized_newsletter` to construct a clean, well-formatted Markdown newsletter containing:
  1. Executive Summary
  2. High-Priority Updates (with GA / Preview badges)
  3. Relevant Platform & Operational Updates
  4. Concrete Action Items & Next Steps
- Present the synthesized newsletter to the user clearly.

### Step 4: Iterative Refinement & Quality Assurance
- Ask the user if they would like any adjustments (e.g. shortening, focusing on security/cost/models, or regenerating for another customer).
- Maintain 100% factual accuracy grounded in official Google Cloud release notes.

Always provide helpful, precise, and professional communication.
"""

root_agent = Agent(
    name="cloud_newsletter_orchestrator",
    model=config.gemini_model,
    instruction=ROOT_ORCHESTRATOR_INSTRUCTION,
    sub_agents=[profiler_agent, curator_agent, synthesizer_agent, critic_agent],
    tools=[
        crm_lookup_tool,
        crm_update_tool,
        fetch_rn_tool,
        rank_rn_tool,
        format_newsletter_tool,
    ],
    before_agent_callback=initialize_newsletter_state,
    after_agent_callback=trace_agent_execution,
)
