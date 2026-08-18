from typing import Any, Dict, List, Optional
from app.observability.tracer import tracer


class HistoryCompactor:
    """Token-aware conversation history and context compaction engine.
    
    Prevents token bloat, maintains critical architectural context, summarizes
    older conversational turns, and retains recent turns in full fidelity.
    """
    
    def __init__(self, max_turns_threshold: int = 4, target_token_budget: int = 2000):
        self.max_turns_threshold = max_turns_threshold
        self.target_token_budget = target_token_budget

    def estimate_tokens(self, text: str) -> int:
        """Heuristic estimation of tokens (avg 4 chars per token)."""
        return max(1, len(text) // 4)

    def compact_history(
        self,
        messages: List[Dict[str, Any]],
        existing_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compacts a message history list by summarizing older turns.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            existing_summary: Prior accumulated summary string.
            
        Returns:
            Dict containing:
                - 'compacted_messages': Kept recent full messages.
                - 'summary': Compacted summary of earlier turns.
                - 'tokens_saved': Estimated number of tokens saved.
        """
        with tracer.trace_span("compact_history", {"total_turns": len(messages)}):
            if len(messages) <= self.max_turns_threshold:
                tracer.info("compactor_skipped", "Message count within threshold; no compaction necessary")
                return {
                    "compacted_messages": messages,
                    "summary": existing_summary,
                    "tokens_saved": 0
                }

            # Split into older turns to summarize and recent turns to preserve
            split_idx = len(messages) - self.max_turns_threshold
            older_turns = messages[:split_idx]
            recent_turns = messages[split_idx:]

            older_tokens = sum(self.estimate_tokens(str(m.get("content", ""))) for m in older_turns)
            
            # Generate structured compact summary
            summary_fragments = []
            if existing_summary:
                summary_fragments.append(f"Prior Context Summary: {existing_summary}")
            
            for idx, msg in enumerate(older_turns, 1):
                role = msg.get("role", "user")
                content = str(msg.get("content", ""))
                snippet = content[:150] + ("..." if len(content) > 150 else "")
                summary_fragments.append(f"Turn {idx} [{role}]: {snippet}")

            new_summary = " | ".join(summary_fragments)
            summary_tokens = self.estimate_tokens(new_summary)
            tokens_saved = max(0, older_tokens - summary_tokens)

            tracer.info(
                "history_compacted",
                f"Compacted {len(older_turns)} older turns into context summary. Saved ~{tokens_saved} tokens.",
                older_turns_count=len(older_turns),
                tokens_saved=tokens_saved
            )

            return {
                "compacted_messages": recent_turns,
                "summary": new_summary,
                "tokens_saved": tokens_saved
            }


history_compactor = HistoryCompactor()
