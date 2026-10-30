from core.schemas import InvoiceData
from core.evidence import verify_invoice_evidence

def test_tax_amount_matches_sum_of_cgst_and_sgst_lines():
    data = InvoiceData(tax_amount=1440)
    result = verify_invoice_evidence(
        data,
        "Subtotal: 8,000.00\nCGST: 720.00\nSGST: 720.00\nGrand Total: 9,440.00"
    )
    assert result.field_confidence["tax_amount"] == 1.0
    assert "CGST: 720.00" in result.field_evidence["tax_amount"]
    assert "SGST: 720.00" in result.field_evidence["tax_amount"]

def test_tax_amount_does_not_match_incorrect_component_sum():
    data = InvoiceData(tax_amount=1500)
    result = verify_invoice_evidence(
        data,
        "CGST: 720.00\nSGST: 720.00"
    )
    assert result.field_confidence["tax_amount"] == 0.0
    assert result.field_evidence["tax_amount"] == ""

def test_single_tax_line_still_matches_directly():
    data = InvoiceData(tax_amount=1440)
    result = verify_invoice_evidence(data, "GST (18%): 1,440.00")
    assert result.field_confidence["tax_amount"] == 1.0
