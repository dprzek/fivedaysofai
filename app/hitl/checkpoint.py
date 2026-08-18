from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.observability.tracer import tracer


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class ApprovalRequest(BaseModel):
    """Encapsulates an operation requiring programmatic Human-in-the-Loop approval."""
    request_id: str = Field(..., description="Unique approval request ID")
    operation_type: str = Field(..., description="Action type (e.g. 'PUBLISH_NEWSLETTER', 'SEND_CUSTOMER_EMAIL')")
    customer_name: str
    summary: str
    payload: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decision_notes: Optional[str] = None
    decided_by: Optional[str] = None


class HITLManager:
    """Human-in-the-Loop governance and approval checkpoint manager.
    
    Ensures high-impact operations like sending emails or publishing public release briefings
    are halted at an explicit checkpoint pending human validation or override.
    """

    def __init__(self):
        self._pending_requests: Dict[str, ApprovalRequest] = {}
        self._history: List[ApprovalRequest] = []

    def request_approval(
        self,
        request_id: str,
        operation_type: str,
        customer_name: str,
        summary: str,
        payload: Dict[str, Any]
    ) -> ApprovalRequest:
        """Creates and registers a new HITL approval checkpoint."""
        with tracer.trace_span("hitl_request_approval", {"request_id": request_id, "operation": operation_type}):
            req = ApprovalRequest(
                request_id=request_id,
                operation_type=operation_type,
                customer_name=customer_name,
                summary=summary,
                payload=payload,
                status=ApprovalStatus.PENDING
            )
            self._pending_requests[request_id] = req
            tracer.info("hitl_checkpoint_created", f"Created HITL checkpoint {request_id} for {operation_type}", request_id=request_id)
            return req

    def process_decision(
        self,
        request_id: str,
        status: ApprovalStatus,
        decided_by: str = "human_operator",
        decision_notes: Optional[str] = None
    ) -> ApprovalRequest:
        """Applies a human approval, rejection, or edit decision to a pending checkpoint."""
        with tracer.trace_span("hitl_process_decision", {"request_id": request_id, "decision": status.value}):
            if request_id not in self._pending_requests:
                raise ValueError(f"Approval request {request_id} not found in pending queue.")
            
            req = self._pending_requests.pop(request_id)
            req.status = status
            req.decided_by = decided_by
            req.decision_notes = decision_notes
            self._history.append(req)
            tracer.info("hitl_decision_recorded", f"Checkpoint {request_id} resolved: {status.value}", status=status.value)
            return req

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Returns all unresolved approval requests."""
        return list(self._pending_requests.values())

    # Method aliases for flexibility
    create_checkpoint = request_approval
    record_decision = process_decision


hitl_manager = HITLManager()

