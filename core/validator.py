from datetime import date
from core.schemas import InvoiceData

def validate_invoice(data: InvoiceData, duplicate: bool = False) -> list[dict]:
    issues = []
    required = {
        "vendor_name": data.vendor_name,
        "invoice_number": data.invoice_number,
        "invoice_date": data.invoice_date,
        "total_amount": data.total_amount,
    }
    for field, value in required.items():
        if value in (None, ""):
            issues.append({"severity": "warning", "code": f"missing_{field}", "message": f"Missing {field.replace('_', ' ')}."})

    if duplicate:
        issues.append({"severity": "error", "code": "duplicate_invoice", "message": "This vendor and invoice number already exist in the database."})

    if data.subtotal is not None and data.tax_amount is not None and data.total_amount is not None:
        calculated = round(data.subtotal + data.tax_amount, 2)
        if abs(calculated - round(data.total_amount, 2)) > 0.02:
            issues.append({"severity": "error", "code": "total_mismatch", "message": f"Subtotal + tax is {calculated:.2f}, but invoice total is {data.total_amount:.2f}."})

    if data.invoice_date:
        try:
            invoice_date = date.fromisoformat(data.invoice_date)
            if data.due_date:
                due_date = date.fromisoformat(data.due_date)
                if due_date < invoice_date:
                    issues.append({"severity": "warning", "code": "date_order", "message": "Due date is earlier than invoice date."})
        except ValueError:
            issues.append({"severity": "warning", "code": "invalid_date", "message": "A date could not be interpreted in ISO YYYY-MM-DD format."})

    return issues
