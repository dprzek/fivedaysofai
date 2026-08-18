from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.config import config
from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile

PROFILER_INSTRUCTIONS = """You are the specialized Customer Profiler Agent.
Your responsibility is to look up customer CRM profiles, identify their active cloud tech stack, architectural priorities, and account tier.
If a customer is not found or details need updating, register or update their profile.

Always return the full customer profile schema with tech_stack and priorities.
"""

profiler_agent = Agent(
    name="customer_profiler_agent",
    model=config.PROFILER_MODEL,
    description="Looks up and analyzes enterprise customer CRM profiles, tech stack, and priorities.",
    instruction=PROFILER_INSTRUCTIONS,
    tools=[
        FunctionTool(lookup_customer_profile),
        FunctionTool(register_or_update_customer_profile),
    ]
)
