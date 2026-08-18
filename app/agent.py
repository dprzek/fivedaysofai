from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.callbacks import initialize_newsletter_state, trace_agent_execution
from app.config import config
from app.sub_agents.critic import critic_agent
from app.sub_agents.curator import curator_agent
from app.sub_agents.profiler import profiler_agent
from app.sub_agents.synthesizer import synthesizer_agent
from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile
from app.tools.publisher import format_newsletter_markdown
from app.tools.release_notes import fetch_cloud_release_notes
from app.tools.relevance_ranker import score_and_rank_release_notes

ORCHESTRATOR_INSTRUCTIONS = """You are the Lead Coordinator for the Personalized Google Cloud Release Notes Newsletter System.
Your mission is to orchestrate specialized sub-agents to deliver highly customized, executive-ready technical briefings for enterprise Google Cloud customers.

### Orchestration Workflow:
1. **Identify & Profile Customer**:
   - Use `customer_profiler_agent` (or `lookup_customer_profile`) to identify the customer's active tech stack, architectural priorities, and account tier.
2. **Curate & Rank Releases**:
   - Use `release_notes_curator_agent` (or `fetch_cloud_release_notes` + `score_and_rank_release_notes`) to retrieve recent Google Cloud / Gemini Enterprise updates and score their architectural relevance.
3. **Synthesize Executive Briefing**:
   - Use `newsletter_synthesizer_agent` (or `format_newsletter_markdown`) to produce a polished markdown newsletter with actionable recommendations.
4. **Fact-Check & Verify**:
   - Use `fact_checking_critic_agent` to review the draft against source facts and customer priorities.
5. **Output Final Result**:
   - Present the verified executive newsletter directly to the user.

Ensure clear, professional communication with tailored architectural recommendations.
"""

agent = Agent(
    name="cloud_newsletter_orchestrator",
    model=config.ORCHESTRATOR_MODEL,
    description="Multi-agent orchestrator curating personalized Google Cloud and Gemini Enterprise release note briefings.",
    instruction=ORCHESTRATOR_INSTRUCTIONS,
    tools=[
        FunctionTool(lookup_customer_profile),
        FunctionTool(register_or_update_customer_profile),
        FunctionTool(fetch_cloud_release_notes),
        FunctionTool(score_and_rank_release_notes),
        FunctionTool(format_newsletter_markdown),
    ],
    sub_agents=[
        profiler_agent,
        curator_agent,
        synthesizer_agent,
        critic_agent,
    ],
    before_agent_callback=initialize_newsletter_state,
    after_agent_callback=trace_agent_execution,
)

# Export root_agent alias
root_agent = agent
