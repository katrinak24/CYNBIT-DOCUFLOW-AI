from core.schemas import InvoiceData
from core.validator import validate_invoice

def test_total_mismatch_is_flagged():
    data = InvoiceData(subtotal=100, tax_amount=18, total_amount=120)
    issues = validate_invoice(data)
    assert any(x["code"] == "total_mismatch" for x in issues)

def test_missing_vendor_is_flagged():
    data = InvoiceData(invoice_number="INV-1", invoice_date="2026-10-30", total_amount=118)
    issues = validate_invoice(data)
    assert any(x["code"] == "missing_vendor_name" for x in issues)

def test_valid_amounts_have_no_total_mismatch():
    data = InvoiceData(subtotal=100, tax_amount=18, total_amount=118)
    issues = validate_invoice(data)
    assert not any(x["code"] == "total_mismatch" for x in issues)
