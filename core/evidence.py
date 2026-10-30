import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from core.schemas import InvoiceData
from core.verification_summary import build_verification_summary

FIELD_NAMES = ["vendor_name", "invoice_number", "invoice_date", "due_date", "currency",
               "subtotal", "tax_amount", "total_amount", "payment_status"]
LABELS = {
    "invoice_number": re.compile(r"\b(?:invoice\s*(?:no\.?|number|#)|inv\.?\s*no\.?)\s*[:#-]?\s*", re.I),
    "invoice_date": re.compile(r"\b(?:invoice\s*date|date\s*of\s*invoice)\s*[:#-]?\s*", re.I),
    "due_date": re.compile(r"\b(?:due\s*date|payment\s*due)\s*[:#-]?\s*", re.I),
    "subtotal": re.compile(r"\b(?:sub\s*total|subtotal|taxable\s*value)\s*[:#-]?\s*", re.I),
    "total_amount": re.compile(r"\b(?:grand\s*total|total\s*amount|amount\s*payable|net\s*payable)\s*[:#-]?\s*", re.I),
    "payment_status": re.compile(r"\b(?:payment\s*status|payment\s*state)\s*[:#-]?\s*", re.I),
    "currency": re.compile(r"\b(?:currency)\s*[:#-]?\s*|\bamount\s*\(\s*(INR|USD|EUR|GBP)\s*\)", re.I),
}
NUM_RE = re.compile(r"(?<![A-Za-z])(?:₹\s*)?-?\d[\d,]*(?:\.\d{1,2})?")
DATE_RE = re.compile(r"\b(?:\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

def _norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().casefold()

def _number(s):
    try:
        return Decimal(str(s).replace(",", "").replace("₹", "").strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None

def _date_forms(value):
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(value, fmt).date()
            return {_norm(parsed.strftime(f)) for f in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%d/%m/%Y", "%d-%m-%Y")}
        except ValueError:
            continue
    return {_norm(value)} if value else set()

def _label_match(field, line):
    pattern = LABELS.get(field)
    return pattern.search(line) if pattern else None

def _compact_label_evidence(field, value, line, match):
    """Return only the label and nearby matched value, excluding OCR-joined neighbours."""
    if field in ("invoice_date", "due_date"):
        candidates = [m.group(0) for m in DATE_RE.finditer(line)]
        expected = _date_forms(value)
        found = next((c for c in candidates if _norm(c) in expected), None)
        return f"{match.group(0).strip()} {found}".strip() if found else ""
    if field in ("subtotal", "total_amount"):
        expected = _number(value)
        candidates = [m.group(0) for m in NUM_RE.finditer(line[match.end():])]
        found = next((c for c in candidates if _number(c) == expected), None)
        return f"{match.group(0).strip()} {found}".strip() if found else ""
    if field == "invoice_number":
        tail = line[match.end():]
        token = re.match(r"\s*([A-Z0-9][A-Z0-9./_-]{2,})", tail, re.I)
        if token and _norm(token.group(1)) == _norm(value):
            return f"{match.group(0).strip()} {token.group(1)}".strip()
        return ""
    if field == "payment_status":
        tail = line[match.end():]
        token = re.match(r"\s*(paid|unpaid|pending|overdue|partially\s+paid)\b", tail, re.I)
        return f"{match.group(0).strip()} {token.group(1)}".strip() if token and _norm(token.group(1)) == _norm(value) else ""
    if field == "currency":
        code = re.search(r"\b(INR|USD|EUR|GBP)\b", line, re.I)
        if code and _norm(code.group(1)) == _norm(value):
            return f"AMOUNT ({code.group(1).upper()})"
        return ""
    return ""

def _tax_components(lines):
    found = []
    pattern = re.compile(r"\b(CGST|SGST|IGST)\b\s*(?:\([^)]*\))?\s*[:=-]\s*((?:₹\s*)?\d[\d,]*(?:\.\d{1,2})?)", re.I)
    for line in lines:
        for m in pattern.finditer(line):
            amount = _number(m.group(2))
            if amount is not None:
                found.append((f"{m.group(1).upper()}: {m.group(2)}", amount))
    return found

def _vendor_evidence(value, lines):
    if not value:
        return []
    target = _norm(value)
    results = []
    for line in lines:
        # Require a supplier phrase in a header-like line, not customer block.
        if target in _norm(line) and not re.search(r"\b(bill\s*to|ship\s*to|customer)\b", line, re.I):
            cleaned = re.sub(r"\b(tax\s+invoice|original\s+for\s+recipient)\b", "", line, flags=re.I)
            cleaned = re.sub(r"\s+", " ", cleaned).strip(" -|:")
            results.append(cleaned or value)
    return results

def verify_invoice_evidence(data: InvoiceData, source_text: str) -> InvoiceData:
    """Field-specific evidence match; a match is not a truth guarantee or probability."""
    lines = [re.sub(r"\s+", " ", x).strip() for x in source_text.splitlines() if x.strip()]
    confidence, evidence, statuses = {}, {}, {}
    for field in FIELD_NAMES:
        value = getattr(data, field)
        matches = []
        if value not in (None, ""):
            if field == "vendor_name":
                matches = _vendor_evidence(value, lines)
            elif field == "tax_amount":
                expected = _number(value)
                components = _tax_components(lines)
                if expected is not None and len(components) >= 2:
                    if sum((amount for _, amount in components), Decimal("0.00")) == expected:
                        matches = [quote for quote, _ in components]
                if not matches:
                    for line in lines:
                        if re.search(r"\b(?:gst|tax)\b", line, re.I):
                            for num in NUM_RE.findall(line):
                                if _number(num) == expected:
                                    matches.append(line[:180])
            else:
                for line in lines:
                    label = _label_match(field, line)
                    if label:
                        quote = _compact_label_evidence(field, value, line, label)
                        if quote:
                            matches.append(quote)
        if matches:
            confidence[field] = 1.0
            evidence[field] = " | ".join(dict.fromkeys(matches))[:500]
            statuses[field] = "Verified"
        elif value in (None, ""):
            confidence[field] = 0.0
            evidence[field] = ""
            statuses[field] = "Needs review"
        else:
            confidence[field] = 0.0
            evidence[field] = ""
            statuses[field] = "Not verified"
    data.field_confidence = confidence
    data.field_evidence = evidence
    data.field_verification = statuses
    data.verification_summary = build_verification_summary(statuses)
    return data
