import json
import sqlite3
import pytest
import database.db as db
from core.schemas import InvoiceData
from utils.export import records_as_rows, json_bytes, csv_bytes

def setup_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "test.db")
    db.init_db()
    return tmp_path / "test.db"

def test_review_saves_corrected_fields_and_status_atomically(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    original = InvoiceData(vendor_name="Wrong Vendor", invoice_number="INV-1", total_amount=100)
    rid = db.save_invoice("invoice.pdf", original, [])
    corrected = InvoiceData(vendor_name="Correct Vendor", invoice_number="INV-1", total_amount=100)
    db.update_invoice_review(rid, corrected, [{"severity":"warning","message":"reviewed"}], "Approved")
    record = db.list_invoices()[0]
    payload = json.loads(record["extracted_json"])
    assert record["status"] == "Approved"
    assert record["vendor_name"] == "Correct Vendor"
    assert payload["vendor_name"] == "Correct Vendor"
    assert json.loads(record["issues_json"])[0]["message"] == "reviewed"

def test_status_rejects_unknown_value(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = InvoiceData(vendor_name="Vendor", invoice_number="INV-1")
    rid = db.save_invoice("invoice.pdf", data, [])
    with pytest.raises(ValueError):
        db.update_status(rid, "Approved-ish")

def test_csv_and_json_exports_use_same_sqlite_status(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = InvoiceData(vendor_name="Vendor", invoice_number="INV-1", total_amount=100)
    rid = db.save_invoice("invoice.pdf", data, [])
    db.update_status(rid, "Approved")
    records = db.list_invoices()
    rows = records_as_rows(records)
    json_records = json.loads(json_bytes(records))
    assert rows[0]["workflow_status"] == "Approved"
    assert json_records[0]["status"] == "Approved"
    assert str(rid) in csv_bytes(records).decode("utf-8-sig")
    assert json_records[0]["vendor_name"] == "Vendor"

def test_export_contains_field_evidence_and_verification(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = InvoiceData(
        vendor_name="Vendor", invoice_number="INV-1",
        field_evidence={"vendor_name":"Vendor header"},
        field_verification={"vendor_name":"Verified"}
    )
    db.save_invoice("invoice.pdf", data, [])
    payload = json.loads(json_bytes())[0]
    assert payload["field_evidence"]["vendor_name"] == "Vendor header"
    assert payload["field_verification"]["vendor_name"] == "Verified"


def test_original_source_text_is_saved_and_retrievable(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    data = InvoiceData(vendor_name="Vendor", invoice_number="INV-2")
    rid = db.save_invoice("invoice.pdf", data, [], source_text="Vendor\\nInvoice Number: INV-2")
    assert db.get_invoice_source(rid) == "Vendor\\nInvoice Number: INV-2"

def test_legacy_database_gets_source_text_column_without_losing_rows(tmp_path, monkeypatch):
    # Build the pre-v3 table shape to exercise the additive migration.
    monkeypatch.setattr(db, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "legacy.db")
    conn = sqlite3.connect(db.DATABASE_PATH)
    conn.execute("""CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL,
        vendor_name TEXT, invoice_number TEXT, total_amount REAL,
        status TEXT NOT NULL DEFAULT 'Pending Review', extracted_json TEXT NOT NULL,
        issues_json TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    conn.execute("INSERT INTO invoices (filename, extracted_json, issues_json, created_at) VALUES ('old.pdf', '{}', '[]', 'now')")
    conn.commit()
    conn.close()
    db.init_db()
    rows = db.list_invoices()
    assert len(rows) == 1
    assert rows[0]["filename"] == "old.pdf"
    assert rows[0]["source_text"] == ""
