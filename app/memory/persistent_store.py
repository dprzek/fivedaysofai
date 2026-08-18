import asyncio
import json
import os
import aiosqlite
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.memory.state_manager import AgentSessionState, CustomerProfile, NewsletterDraft
from app.observability.tracer import tracer


class AsyncDatabaseSessionStore:
    """Enterprise asynchronous database session store for agent state persistence.
    
    Provides ACID-compliant persistence for multi-turn conversational agent sessions,
    customer profiles, release curation runs, and newsletter drafts using SQLite / Cloud SQL.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = Path(os.getenv("AGENT_DATA_DIR", "/tmp/newsletter_agent_data"))
            base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(base_dir / "agent_sessions.db")
        else:
            self.db_path = db_path
        self._initialized = False

    async def initialize(self) -> None:
        """Initializes the database schema if not already present."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    customer_name TEXT,
                    state_json TEXT NOT NULL,
                    turn_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS newsletter_archives (
                    archive_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    customer_name TEXT,
                    title TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                );
            """)
            await db.commit()
        self._initialized = True
        tracer.info("database_store_initialized", f"Session database initialized at {self.db_path}")

    async def save_session_state(self, session_id: str, state: AgentSessionState) -> None:
        """Persists agent session state asynchronously to database."""
        await self.initialize()
        state_payload = state.model_dump_json()
        now = datetime.now(timezone.utc).isoformat()
        
        with tracer.trace_span("db_save_session_state", {"session_id": session_id, "customer": state.customer_name}):
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO sessions (session_id, customer_name, state_json, turn_count, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        customer_name = excluded.customer_name,
                        state_json = excluded.state_json,
                        turn_count = excluded.turn_count,
                        updated_at = excluded.updated_at;
                """, (session_id, state.customer_name, state_payload, state.turn_count, now))
                await db.commit()
            tracer.info("session_persisted", f"Session {session_id} successfully persisted", session_id=session_id)

    async def load_session_state(self, session_id: str) -> Optional[AgentSessionState]:
        """Loads and deserializes an agent session state from the database."""
        await self.initialize()
        with tracer.trace_span("db_load_session_state", {"session_id": session_id}):
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT state_json FROM sessions WHERE session_id = ?",
                    (session_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        raw_json = row[0]
                        data = json.loads(raw_json)
                        tracer.info("session_loaded", f"Loaded session {session_id} from database", session_id=session_id)
                        return AgentSessionState(**data)
            tracer.info("session_not_found", f"No existing session found for {session_id}", session_id=session_id)
            return None

    async def list_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lists recent sessions stored in database."""
        await self.initialize()
        results = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT session_id, customer_name, turn_count, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ) as cursor:
                async for row in cursor:
                    results.append({
                        "session_id": row[0],
                        "customer_name": row[1],
                        "turn_count": row[2],
                        "updated_at": row[3]
                    })
        return results


persistent_session_store = AsyncDatabaseSessionStore()
