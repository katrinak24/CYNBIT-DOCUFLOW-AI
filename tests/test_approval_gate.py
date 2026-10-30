from core.schemas import InvoiceData
from core.approval import approval_blockers


def fully_verified_data():
    return InvoiceData(
        vendor_name="Northstar", invoice_number="NS-1", invoice_date="2026-10-30",
        due_date="2026-11-14", currency="INR", total_amount=100, payment_status="UNPAID",
        field_verification={
            "vendor_name":"Verified", "invoice_number":"Verified",
            "invoice_date":"Verified", "due_date":"Needs review",
            "currency":"Verified", "subtotal":"Verified",
            "tax_amount":"Verified", "total_amount":"Verified",
            "payment_status":"Needs review"
        }
    )


def test_approval_blocks_missing_required_vendor():
    data = fully_verified_data()
    data.vendor_name = None
    assert "vendor_name" in approval_blockers(data)


def test_approval_blocks_populated_unverified_field():
    data = fully_verified_data()
    assert "due_date" in approval_blockers(data)


def test_approval_allows_missing_optional_fields_but_requires_populated_evidence():
    data = fully_verified_data()
    data.field_verification["due_date"] = "Not evaluated"
    data.field_verification["payment_status"] = "Not evaluated"
    data.due_date = None
    data.payment_status = None
    assert approval_blockers(data) == []


def test_approval_allows_fully_verified_required_fields():
    data = fully_verified_data()
    data.field_verification["due_date"] = "Verified"
    data.field_verification["payment_status"] = "Verified"
    assert approval_blockers(data) == []
