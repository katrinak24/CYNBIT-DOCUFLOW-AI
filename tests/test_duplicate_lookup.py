from database.db import init_db, save_invoice, find_duplicate
from core.schemas import InvoiceData
import database.db as db_module

def test_find_duplicate_returns_existing_record(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db_module, "DATABASE_PATH", tmp_path / "test.db")
    init_db()
    data = InvoiceData(vendor_name="ABC Technologies", invoice_number="INV-001", total_amount=100)
    record_id = save_invoice("one.pdf", data, [])
    found = find_duplicate("abc technologies", "inv-001")
    assert found["id"] == record_id
    assert found["filename"] == "one.pdf"

def test_find_duplicate_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DATABASE_DIR", tmp_path)
    monkeypatch.setattr(db_module, "DATABASE_PATH", tmp_path / "test.db")
    init_db()
    assert find_duplicate("Unknown", "INV-404") is None
