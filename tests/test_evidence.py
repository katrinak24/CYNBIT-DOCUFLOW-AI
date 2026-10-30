from core.schemas import InvoiceData
from core.evidence import verify_invoice_evidence

def test_exact_text_evidence_is_found():
    data = InvoiceData(vendor_name="ABC Technologies Private Limited",
                       invoice_number="ABC-2026-001", total_amount=11800)
    result = verify_invoice_evidence(
        data,
        "ABC Technologies Private Limited\nInvoice Number: ABC-2026-001\nGrand Total: 11800.00"
    )
    assert result.field_confidence["vendor_name"] == 1.0
    assert result.field_confidence["invoice_number"] == 1.0
    assert result.field_confidence["total_amount"] == 1.0
    assert "Grand Total" in result.field_evidence["total_amount"]

def test_missing_evidence_is_not_claimed():
    data = InvoiceData(vendor_name="Invented Vendor", total_amount=900)
    result = verify_invoice_evidence(data, "ABC Technologies\nGrand Total: 11800.00")
    assert result.field_confidence["vendor_name"] == 0.0
    assert result.field_evidence["vendor_name"] == ""
    assert result.field_confidence["total_amount"] == 0.0

def test_date_evidence_supports_iso_value():
    data = InvoiceData(invoice_date="2026-10-30")
    result = verify_invoice_evidence(data, "Invoice Date: 30 October 2026")
    assert result.field_confidence["invoice_date"] == 1.0

def test_numeric_evidence_supports_decimal_format():
    data = InvoiceData(subtotal=10000)
    result = verify_invoice_evidence(data, "Subtotal: 10,000.00")
    assert result.field_confidence["subtotal"] == 1.0
