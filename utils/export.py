import json
import pandas as pd
from database.db import list_invoices, list_verification_audit
from core.verification_summary import resolve_verification


def _record_payload(record):
    extracted = json.loads(record["extracted_json"])
    issues = json.loads(record["issues_json"])
    verification, summary = resolve_verification(extracted)
    extracted["field_verification"] = verification
    extracted["verification_summary"] = summary
    return {
        "id": record["id"],
        "filename": record["filename"],
        **extracted,
        "status": record["status"],
        "issues": issues,
        "created_at": record["created_at"],
        "source_text_available": bool(record.get("source_text")),
        "verification_audit": [
            {
                "audit_id": item["audit_id"],
                "source_filename": item["source_filename"],
                "original_workflow_status": item["original_workflow_status"],
                "created_at": item["created_at"],
                "source_text_sha256": item["source_text_sha256"],
                "new_verification": json.loads(item["new_verification_json"]),
            }
            for item in list_verification_audit(record["id"])
        ],
    }


def records_as_rows(records=None):
    records = list_invoices() if records is None else records
    rows = []
    for record in records:
        item = json.loads(record["extracted_json"])
        verification, summary = resolve_verification(item)
        evidence = item.get("field_evidence", {}) or {}
        issues = json.loads(record["issues_json"])
        audits = list_verification_audit(record["id"])
        rows.append({
            "id": record["id"],
            "filename": record["filename"],
            "vendor_name": record["vendor_name"],
            "invoice_number": record["invoice_number"],
            "invoice_date": item.get("invoice_date"),
            "due_date": item.get("due_date"),
            "currency": item.get("currency"),
            "subtotal": item.get("subtotal"),
            "tax_amount": item.get("tax_amount"),
            "total_amount": record["total_amount"],
            "payment_status": item.get("payment_status"),
            "workflow_status": record["status"],
            "verified_fields": summary["verified_fields"],
            "fields_needing_review": summary["fields_needing_review"],
            "fields_not_verified": summary["fields_not_verified"],
            "fields_not_evaluated": summary["fields_not_evaluated"],
            "total_fields": summary["total_fields"],
            "verification_status": summary["status"],
            "source_text_available": bool(record.get("source_text")),
            "reverification_count": len(audits),
            "last_reverified_at": audits[0]["created_at"] if audits else "",
            "evidence_json": json.dumps(evidence, ensure_ascii=False),
            "field_verification_json": json.dumps(verification, ensure_ascii=False),
            "issues": "; ".join(x.get("message", "") for x in issues),
            "created_at": record["created_at"],
        })
    return rows


def csv_bytes(records=None):
    return pd.DataFrame(records_as_rows(records)).to_csv(index=False).encode("utf-8-sig")


def json_bytes(records=None):
    records = list_invoices() if records is None else records
    return json.dumps([_record_payload(r) for r in records], indent=2, ensure_ascii=False).encode("utf-8")
