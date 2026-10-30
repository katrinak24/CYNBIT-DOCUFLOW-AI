import json
import database.db as db
from core.schemas import InvoiceData
from utils.export import records_as_rows, json_bytes

def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "export-v4.db")
    db.init_db()

def test_csv_counts_legacy_records_as_not_evaluated(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    legacy = InvoiceData(vendor_name="Old Vendor", invoice_number="OLD-1", total_amount=100)
    db.save_invoice("legacy.pdf", legacy, [])
    row = records_as_rows()[0]
    assert row["verification_status"] == "Not evaluated"
    assert row["verified_fields"] == 0
    assert row["fields_not_evaluated"] == 9

def test_csv_counts_v3_confidence_and_evidence_when_verification_map_missing(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    data = InvoiceData(
        vendor_name="Northstar",
        invoice_number="NS-1",
        invoice_date="2026-10-30",
        due_date="2026-11-14",
        currency="INR",
        subtotal=8000,
        tax_amount=1440,
        total_amount=9440,
        payment_status="UNPAID",
        field_confidence={field: 1.0 for field in (
            "vendor_name","invoice_number","invoice_date","due_date","currency",
            "subtotal","tax_amount","total_amount","payment_status")},
        field_evidence={field: f"source {field}" for field in (
            "vendor_name","invoice_number","invoice_date","due_date","currency",
            "subtotal","tax_amount","total_amount","payment_status")},
    )
    db.save_invoice("northstar.pdf", data, [])
    row = records_as_rows()[0]
    assert row["verification_status"] == "Verified"
    assert row["verified_fields"] == 9
    assert row["fields_not_evaluated"] == 0

def test_csv_counts_partial_verification_without_inflating_total(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    data = InvoiceData(
        vendor_name=None,
        invoice_number="NS-1",
        field_confidence={"invoice_number": 1.0, "vendor_name": 0.0},
        field_evidence={"invoice_number": "Invoice Number: NS-1", "vendor_name": ""},
    )
    db.save_invoice("partial.pdf", data, [])
    row = records_as_rows()[0]
    assert row["verified_fields"] == 1
    assert row["fields_needing_review"] == 1
    assert row["fields_not_verified"] == 0
    assert row["fields_not_evaluated"] == 7
    assert row["verification_status"] == "Partially evaluated"

def test_json_and_csv_share_verification_summary(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    data = InvoiceData(
        vendor_name="Northstar",
        invoice_number="NS-1",
        field_confidence={"vendor_name": 1.0, "invoice_number": 1.0},
        field_evidence={"vendor_name": "Northstar", "invoice_number": "Invoice Number: NS-1"},
    )
    db.save_invoice("invoice.pdf", data, [])
    row = records_as_rows()[0]
    payload = json.loads(json_bytes())[0]
    assert row["verified_fields"] == payload["verification_summary"]["verified_fields"] == 2
    assert row["verification_status"] == payload["verification_summary"]["status"]
    assert payload["field_verification"]["vendor_name"] == "Verified"
