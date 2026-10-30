import pytest
from pydantic import ValidationError
from core.schemas import InvoiceData

def test_confidence_accepts_values_between_zero_and_one():
    data = InvoiceData(field_confidence={"vendor_name": 0.95, "total_amount": 0.8})
    assert data.field_confidence["vendor_name"] == 0.95

def test_confidence_rejects_value_above_one():
    with pytest.raises(ValidationError):
        InvoiceData(field_confidence={"total_amount": 1.2})

def test_old_invoice_json_remains_compatible():
    # Existing SQLite records created before confidence fields were added
    # should still load because the new fields have safe defaults.
    data = InvoiceData.model_validate({
        "vendor_name": "ABC Technologies Private Limited",
        "invoice_number": "ABC-2026-001",
        "total_amount": 11800
    })
    assert data.field_confidence == {}
    assert data.field_evidence == {}
