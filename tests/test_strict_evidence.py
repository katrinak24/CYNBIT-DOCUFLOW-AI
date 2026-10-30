from core.schemas import InvoiceData
from core.evidence import verify_invoice_evidence

OCR_TEXT = '''
NORTHSTAR OFFICE SUPPLIES TAX INVOICE
24 Industrial Estate, Sector 18, Gurugram
Invoice Number: NS-2026-1048 BILL TO Demo Customer Pvt. Ltd.
Invoice Date: 30 October 2026 Demo Customer Pvt. Ltd.
Due Date: 14 November 2026
DESCRIPTION QTY UNIT PRICE AMOUNT (INR)
Subtotal: 8,000.00
CGST: 720.00 | SGST: 720.00
Grand Total: 9,440.00
Payment Status: UNPAID
'''

def test_vendor_evidence_is_supplier_phrase_not_bill_to_block():
    data = InvoiceData(vendor_name="NORTHSTAR OFFICE SUPPLIES")
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["vendor_name"] == "Verified"
    assert result.field_evidence["vendor_name"] == "NORTHSTAR OFFICE SUPPLIES"
    assert "TAX INVOICE" not in result.field_evidence["vendor_name"]

def test_invoice_number_requires_invoice_number_label():
    data = InvoiceData(invoice_number="NS-2026-1048")
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["invoice_number"] == "Verified"
    assert result.field_evidence["invoice_number"].startswith("Invoice Number:")

def test_date_evidence_uses_labelled_line_even_when_ocr_joins_customer_text():
    data = InvoiceData(invoice_date="2026-10-30")
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["invoice_date"] == "Verified"
    assert result.field_evidence["invoice_date"].startswith("Invoice Date:")

def test_currency_requires_currency_context():
    data = InvoiceData(currency="INR")
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["currency"] == "Verified"
    assert "AMOUNT (INR)" in result.field_evidence["currency"]

def test_tax_aggregates_cgst_and_sgst_lines():
    data = InvoiceData(tax_amount=1440)
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["tax_amount"] == "Verified"
    assert "CGST: 720.00" in result.field_evidence["tax_amount"]
    assert "SGST: 720.00" in result.field_evidence["tax_amount"]

def test_wrong_tax_sum_is_not_verified():
    data = InvoiceData(tax_amount=1500)
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["tax_amount"] == "Not verified"
    assert result.field_evidence["tax_amount"] == ""

def test_missing_field_is_needs_review():
    data = InvoiceData(vendor_name=None)
    result = verify_invoice_evidence(data, OCR_TEXT)
    assert result.field_verification["vendor_name"] == "Needs review"


from core.schemas import InvoiceData
from core.evidence import verify_invoice_evidence

def test_invoice_number_evidence_excludes_bill_to_customer():
    data = InvoiceData(invoice_number="NS-2026-1048")
    result = verify_invoice_evidence(data, "Invoice Number: NS-2026-1048 BILL TO Demo Customer Pvt. Ltd.")
    assert result.field_verification["invoice_number"] == "Verified"
    assert result.field_evidence["invoice_number"] == "Invoice Number: NS-2026-1048"
    assert "BILL TO" not in result.field_evidence["invoice_number"]

def test_date_evidence_excludes_joined_customer_name():
    data = InvoiceData(invoice_date="2026-10-30")
    result = verify_invoice_evidence(data, "Invoice Date: 30 October 2026 Demo Customer Pvt. Ltd.")
    assert result.field_verification["invoice_date"] == "Verified"
    assert result.field_evidence["invoice_date"] == "Invoice Date: 30 October 2026"
    assert "Demo Customer" not in result.field_evidence["invoice_date"]
