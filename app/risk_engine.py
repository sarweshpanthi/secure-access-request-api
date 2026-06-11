def evaluate_access_request(role: str, justification: str) -> dict:
    """
    Evaluates access request using simple least-privilege rules
    """

    role = role.lower().strip()
    justification = justification.strip()

    if not justification:
        return {
            "risk": "rejected",
            "decision": "rejected",
            "reason": "Access requests must include a business justification."
        }

    high_risk_roles = ["admin", "owner", "production-write", "superuser"]
    medium_risk_roles = ["write", "developer", "editor"]

    if role in high_risk_roles:
        return {
            "risk": "high",
            "decision": "manual_review_required",
            "reason": "Privileged access requires manual review."
        }

    if role in medium_risk_roles:
        return {
            "risk": "medium",
            "decision": "manager_approval_required",
            "reason": "Write-level access requires approval."
        }

    return {
        "risk": "low",
        "decision": "approved_for_review",
        "reason": "Read-only or low-privilege access can proceed through standard review."
    }
