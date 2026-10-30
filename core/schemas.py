from pydantic import BaseModel, Field, field_validator
from typing import Optional

class LineItem(BaseModel):
    description: str = ""
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0

class InvoiceData(BaseModel):
    document_type: str = "invoice"
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: str = "INR"
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    payment_status: Optional[str] = None
    line_items: list[LineItem] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)

    # Evidence-match metadata populated by core.evidence, not trusted LLM confidence.
    field_confidence: dict[str, float] = Field(default_factory=dict)
    field_evidence: dict[str, str] = Field(default_factory=dict)
    field_verification: dict[str, str] = Field(default_factory=dict)
    verification_summary: dict = Field(default_factory=dict)

    @field_validator("field_confidence")
    @classmethod
    def validate_confidence_values(cls, values):
        for field_name, score in values.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(
                    f"Evidence score for {field_name} must be between 0 and 1."
                )
        return values
