import pytest
from app.hitl.checkpoint import HITLManager, ApprovalStatus


def test_hitl_lifecycle():
    manager = HITLManager()
    
    # 1. Create approval request
    req = manager.request_approval(
        request_id="req-001",
        operation_type="PUBLISH_NEWSLETTER",
        customer_name="FinTech Global Bank",
        summary="Newsletter briefing ready for release",
        payload={"draft_id": "draft-123"}
    )
    assert req.status == ApprovalStatus.PENDING
    assert len(manager.get_pending_requests()) == 1

    # 2. Approve request
    resolved = manager.process_decision(
        request_id="req-001",
        status=ApprovalStatus.APPROVED,
        decided_by="lead_cloud_architect",
        decision_notes="Verified executive tone and Spanner recommendations."
    )
    assert resolved.status == ApprovalStatus.APPROVED
    assert resolved.decided_by == "lead_cloud_architect"
    assert len(manager.get_pending_requests()) == 0


def test_hitl_invalid_id():
    manager = HITLManager()
    with pytest.raises(ValueError):
        manager.process_decision("non-existent-id", ApprovalStatus.REJECTED)
