from app.risk_engine import evaluate_access_request


def test_rejects_missing_justification():
    result = evaluate_access_request("admin", "")
    assert result["risk"] == "rejected"
    assert result["decision"] == "rejected"


def test_admin_role_is_high_risk():
    result = evaluate_access_request("admin", "Need access for incident response")
    assert result["risk"] == "high"
    assert result["decision"] == "manual_review_required"


def test_write_role_is_medium_risk():
    result = evaluate_access_request("write", "Need to update configuration")
    assert result["risk"] == "medium"
    assert result["decision"] == "manager_approval_required"


def test_read_only_role_is_low_risk():
    result = evaluate_access_request("read-only", "Need to view logs")
    assert result["risk"] == "low"
    assert result["decision"] == "approved_for_review"