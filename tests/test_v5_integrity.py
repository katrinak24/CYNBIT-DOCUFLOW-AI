import json
import sqlite3
import pytest
import database.db as db
from core.schemas import InvoiceData
from core.evidence import verify_invoice_evidence
from core.verification_summary import build_verification_summary, normalize_verification
from utils.export import records_as_rows, json_bytes, csv_bytes

SOURCE = """NORTHSTAR OFFICE SUPPLIES TAX INVOICE
Invoice Number: NS-2026-1048
Invoice Date: 30 October 2026
Due Date: 14 November 2026
AMOUNT (INR)
Subtotal: 8,000.00
CGST: 720.00 | SGST: 720.00
Grand Total: 9,440.00
Payment Status: UNPAID"""

def setup_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "v5.db")
    db.init_db()
    return tmp_path / "v5.db"

def sample_data():
    data = InvoiceData(
        vendor_name="NORTHSTAR OFFICE SUPPLIES",
        invoice_number="NS-2026-1048",
        invoice_date="2026-10-30",
        due_date="2026-11-14",
        currency="INR",
        subtotal=8000,
        tax_amount=1440,
        total_amount=9440,
        payment_status="UNPAID",
    )
    return verify_invoice_evidence(data, SOURCE)

def test_legacy_verification_summary_is_not_evaluated():
    result = build_verification_summary({})
    assert result == {
        "verified_fields": 0,
        "fields_needing_review": 0,
        "fields_not_verified": 0,
        "fields_not_evaluated": 9,
        "total_fields": 9,
        "status": "Not evaluated",
    }

def test_partial_verification_completes_missing_fields_as_not_evaluated():
    statuses = normalize_verification({"vendor_name": "Verified"})
    assert statuses["vendor_name"] == "Verified"
    assert statuses["invoice_number"] == "Not evaluated"
    result = build_verification_summary(statuses)
    assert result["verified_fields"] == 1
    assert result["fields_not_evaluated"] == 8
    assert result["status"] == "Needs review"

def test_reverification_preserves_approved_status_and_invoice_values(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    original = sample_data()
    record_id = db.save_invoice("scan.pdf", original, [], status="Approved")
    changed_evidence = InvoiceData.model_validate_json(original.model_dump_json())
    changed_evidence.field_evidence["vendor_name"] = "NORTHSTAR OFFICE SUPPLIES"
    outcome = db.update_invoice_evidence(record_id, changed_evidence, SOURCE, "scan.pdf")
    record = db.list_invoices()[0]
    extracted = json.loads(record["extracted_json"])
    assert record["status"] == "Approved"
    assert extracted["vendor_name"] == "NORTHSTAR OFFICE SUPPLIES"
    assert extracted["total_amount"] == 9440
    assert extracted["field_verification"]["vendor_name"] == "Verified"
    assert outcome["workflow_status"] == "Approved"
    assert db.get_invoice_source(record_id) == SOURCE

def test_reverification_writes_append_only_audit(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = sample_data()
    record_id = db.save_invoice("scan.pdf", data, [], status="Pending Review")
    db.update_invoice_evidence(record_id, data, SOURCE, "scan.pdf")
    db.update_invoice_evidence(record_id, data, SOURCE + "\nExtra note", "scan-v2.pdf")
    events = db.list_verification_audit(record_id)
    assert len(events) == 2
    assert events[0]["source_filename"] == "scan-v2.pdf"
    assert events[1]["source_filename"] == "scan.pdf"
    assert all(e["original_workflow_status"] == "Pending Review" for e in events)

def test_exports_mark_legacy_fields_not_evaluated(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    legacy = InvoiceData(vendor_name="Legacy Vendor", invoice_number="OLD-1")
    db.save_invoice("legacy.pdf", legacy, [], status="Approved")
    records = db.list_invoices()
    row = records_as_rows(records)[0]
    payload = json.loads(json_bytes(records))[0]
    assert row["verification_status"] == "Not evaluated"
    assert row["fields_not_evaluated"] == 9
    assert row["fields_needing_review"] == 0
    assert payload["verification_summary"]["status"] == "Not evaluated"
    assert set(payload["field_verification"].values()) == {"Not evaluated"}

def test_exports_include_audit_event_and_preserve_workflow_status(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = sample_data()
    record_id = db.save_invoice("scan.pdf", data, [], status="Approved")
    db.update_invoice_evidence(record_id, data, SOURCE, "scan.pdf")
    records = db.list_invoices()
    row = records_as_rows(records)[0]
    payload = json.loads(json_bytes(records))[0]
    assert row["workflow_status"] == "Approved"
    assert row["reverification_count"] == 1
    assert payload["status"] == "Approved"
    assert len(payload["verification_audit"]) == 1
