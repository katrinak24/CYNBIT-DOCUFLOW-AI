from core.verification_summary import FIELD_NAMES

REQUIRED_FIELDS = ("vendor_name", "invoice_number", "invoice_date", "total_amount")


def approval_blockers(data, verification: dict | None = None) -> list[str]:
    """Return required missing fields and populated fields lacking evidence."""
    verification = verification or getattr(data, "field_verification", {}) or {}
    blockers = []
    for field in REQUIRED_FIELDS:
        value = getattr(data, field, None)
        if value in (None, ""):
            blockers.append(field)
    for field in FIELD_NAMES:
        value = getattr(data, field, None)
        if value not in (None, "") and verification.get(field) != "Verified":
            if field not in blockers:
                blockers.append(field)
    return blockers
