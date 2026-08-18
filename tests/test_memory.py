import asyncio
import pytest
from app.memory.compactor import HistoryCompactor
from app.memory.persistent_store import AsyncDatabaseSessionStore
from app.memory.background_tasks import BackgroundMemoryWorker
from app.memory.state_manager import AgentSessionState, CustomerProfile


def test_history_compactor():
    compactor = HistoryCompactor(max_turns_threshold=2)
    messages = [
        {"role": "user", "content": "Hello, I am from FinTech Bank."},
        {"role": "assistant", "content": "Nice to meet you. Looking up your CRM profile now."},
        {"role": "user", "content": "Please curate release notes for GKE and Spanner."},
        {"role": "assistant", "content": "Here is the curated release notes briefing."}
    ]
    
    result = compactor.compact_history(messages)
    assert len(result["compacted_messages"]) == 2
    assert "FinTech Bank" in result["summary"]
    assert result["tokens_saved"] >= 0


@pytest.mark.asyncio
async def test_async_database_session_store(tmp_path):
    db_file = str(tmp_path / "test_sessions.db")
    store = AsyncDatabaseSessionStore(db_path=db_file)
    
    session_id = "test-session-123"
    profile = CustomerProfile(name="FinTech Global Bank", tech_stack=["Spanner"])
    state = AgentSessionState(customer_name="FinTech Global Bank", customer_profile=profile, turn_count=1)
    
    await store.save_session_state(session_id, state)
    
    loaded = await store.load_session_state(session_id)
    assert loaded is not None
    assert loaded.customer_name == "FinTech Global Bank"
    assert loaded.customer_profile.name == "FinTech Global Bank"
    assert loaded.turn_count == 1


def test_background_worker():
    worker = BackgroundMemoryWorker()
    
    def sync_calc(x, y):
        return x + y
    
    future = worker.run_in_thread(sync_calc, 10, 20, task_name="test_addition")
    assert future.result(timeout=2.0) == 30
