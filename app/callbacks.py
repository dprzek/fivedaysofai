from typing import Any
from google.adk.agents.callback_context import CallbackContext
from app.observability.tracer import tracer


async def initialize_newsletter_state(callback_context: CallbackContext) -> None:
    """Initializes session state variables to prevent KeyError exceptions across conversation turns."""
    state = callback_context.state
    if "customer_name" not in state:
        state["customer_name"] = ""
    if "customer_profile" not in state:
        state["customer_profile"] = None
    if "release_notes" not in state:
        state["release_notes"] = []
    if "curated_items" not in state:
        state["curated_items"] = []
    if "newsletter_draft" not in state:
        state["newsletter_draft"] = None
    if "conversation_turn" not in state:
        state["conversation_turn"] = 0
    if "user_feedback" not in state:
        state["user_feedback"] = []
        
    state["conversation_turn"] += 1
    tracer.info(
        "session_state_initialized",
        f"Session state initialized/updated for turn {state['conversation_turn']}",
        turn=state["conversation_turn"],
        customer=state.get("customer_name")
    )


async def trace_agent_execution(callback_context: CallbackContext) -> None:
    """Logs after-agent turn telemetry, tracking state changes and latency."""
    state = callback_context.state
    tracer.info(
        "after_agent_turn",
        f"Completed agent execution for turn {state.get('conversation_turn', 1)}",
        has_profile=state.get("customer_profile") is not None,
        has_draft=state.get("newsletter_draft") is not None,
    )
