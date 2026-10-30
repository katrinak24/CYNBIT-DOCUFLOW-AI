from __future__ import annotations

FIELD_NAMES = [
    "vendor_name", "invoice_number", "invoice_date", "due_date", "currency",
    "subtotal", "tax_amount", "total_amount", "payment_status",
]
VALID_VERIFICATION_STATES = {"Verified", "Needs review", "Not verified", "Not evaluated"}


def normalize_verification(statuses: dict | None) -> dict[str, str]:
    """Return a complete per-field state map; absent legacy fields are Not evaluated."""
    statuses = statuses or {}
    result = {}
    for field in FIELD_NAMES:
        state = statuses.get(field, "Not evaluated")
        result[field] = state if state in VALID_VERIFICATION_STATES else "Not evaluated"
    return result


def derive_verification_from_evidence(extracted: dict) -> dict[str, str]:
    """Backfill v3 evidence metadata when a newer field_verification map is absent.

    This deliberately does not infer verification for older records without any
    confidence/evidence metadata. A field is Verified only when its value is
    populated, confidence is at least 1.0, and a non-empty evidence quote exists.
    """
    confidence = extracted.get("field_confidence") or {}
    evidence = extracted.get("field_evidence") or {}
    has_legacy_metadata = bool(confidence) or bool(evidence)
    if not has_legacy_metadata:
        return normalize_verification(None)

    states = {}
    for field in FIELD_NAMES:
        has_confidence = field in confidence
        has_evidence = field in evidence
        if not has_confidence and not has_evidence:
            states[field] = "Not evaluated"
            continue

        value = extracted.get(field)
        quote = evidence.get(field, "")
        try:
            score = float(confidence.get(field, 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0

        if value in (None, ""):
            states[field] = "Needs review"
        elif score >= 1.0 and isinstance(quote, str) and quote.strip():
            states[field] = "Verified"
        elif isinstance(quote, str) and quote.strip():
            states[field] = "Not verified"
        elif has_confidence or has_evidence:
            states[field] = "Not verified"
        else:
            states[field] = "Not evaluated"
    return normalize_verification(states)


def resolve_verification(extracted: dict) -> tuple[dict[str, str], dict[str, int | str]]:
    """Resolve explicit v5 states or derive compatible states from v3 metadata."""
    explicit = extracted.get("field_verification")
    if isinstance(explicit, dict) and explicit:
        statuses = normalize_verification(explicit)
        summary = build_verification_summary(statuses)
        return statuses, summary

    statuses = derive_verification_from_evidence(extracted)
    summary = build_verification_summary(statuses)
    evaluated = summary["verified_fields"] + summary["fields_needing_review"] + summary["fields_not_verified"]
    if evaluated and summary["fields_not_evaluated"]:
        summary["status"] = "Partially evaluated"
    return statuses, summary


def build_verification_summary(statuses: dict | None) -> dict[str, int | str]:
    normalised = normalize_verification(statuses)
    counts = {
        "verified_fields": sum(v == "Verified" for v in normalised.values()),
        "fields_needing_review": sum(v == "Needs review" for v in normalised.values()),
        "fields_not_verified": sum(v == "Not verified" for v in normalised.values()),
        "fields_not_evaluated": sum(v == "Not evaluated" for v in normalised.values()),
        "total_fields": len(FIELD_NAMES),
    }
    if counts["verified_fields"] == len(FIELD_NAMES):
        status = "Verified"
    elif counts["fields_not_evaluated"] == len(FIELD_NAMES):
        status = "Not evaluated"
    else:
        status = "Needs review"
    counts["status"] = status
    return counts
