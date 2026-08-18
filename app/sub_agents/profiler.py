from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.config import config
from app.tools.customer_crm import lookup_customer_profile, register_or_update_customer_profile

profiler_crm_tool = FunctionTool(func=lookup_customer_profile)
profiler_update_tool = FunctionTool(func=register_or_update_customer_profile)

PROFILER_INSTRUCTION = """
You are the Customer Profiler Agent for the Google Cloud & Gemini Enterprise Newsletter System.

Your primary mission:
1. Identify the enterprise customer name from the conversation or ask the user for it if missing.
2. Use `lookup_customer_profile` to retrieve the customer's industry, tech stack, current infrastructure, and strategic priorities.
3. If new details are provided by the user (e.g., new priorities, upcoming migration, specific pain points), use `register_or_update_customer_profile` to update the profile.
4. Summarize the customer's profile clearly to the user, highlighting key focus areas that will guide the release notes curation.

Always be concise, professional, and ensure you have accurately identified the customer before proceeding.
"""

profiler_agent = Agent(
    name="customer_profiler_agent",
    model=config.gemini_model,
    instruction=PROFILER_INSTRUCTION,
    tools=[profiler_crm_tool, profiler_update_tool],
)
