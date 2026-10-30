# AI Opportunity Report
## DocuFlow AI - Intelligent Invoice Extraction and Exception Review

**Prepared for:** Cynbit Technologies - AI/ML Engineer Intern Assessment  
**Prepared on:** 30 October 2026  
**Project type:** Local-first proof of concept using synthetic invoice data

---

## 1. Executive summary

Cynbit publicly describes LLM automation for manual data entry and document handling as part of its AI automation services. Its AI/ML Engineer Intern role also explicitly identifies document extraction and processing pipelines as a responsibility. These two public signals make document intelligence a directly relevant opportunity to explore.

This report proposes **DocuFlow AI**, an invoice-intake and review workflow that converts PDF/image invoices into structured records, checks extracted values against source text, applies basic financial consistency rules, detects duplicate invoice identifiers, and routes records through human approval.

The proof of concept demonstrates a practical pipeline using Python, PyMuPDF, Tesseract OCR, Ollama/Qwen2.5, Pydantic, SQLite, and Streamlit. The demonstration uses synthetic invoices; it does not use Cynbit's internal documents or claim to measure internal business performance.

## 2. Public company context and assessment alignment

The official Cynbit Services page describes an AI automation suite that includes autonomous agents, LLM automation for manual data entry and document handling, voice agents, and AI-stack integration. The official AI/ML Engineer Intern listing names document extraction and processing pipelines, prompt engineering, chatbots/virtual assistants, and Python/ML/LLM familiarity among the role responsibilities and requirements.

This makes document processing a stronger assessment choice than an unrelated predictive model: it connects a public service capability to an explicit internship responsibility and can be demonstrated end-to-end with a working prototype.

**Public evidence:**

1. Cynbit Technologies, AI Automation & Software Development Services: https://www.cynbit.in/services
2. Cynbit Technologies, AI/ML Engineer Intern: https://www.cynbit.in/careers/ai-ml-engineer-intern
3. Cynbit Technologies, Careers: https://www.cynbit.in/careers

These pages were reviewed on 30 October 2026. Public website descriptions are treated as evidence of advertised services and role expectations, not proof of internal operational pain points.

## 3. Opportunity statement

**Opportunity hypothesis:** Businesses that receive invoices in mixed PDF and image formats can reduce repetitive manual data-entry work by extracting invoice fields into a structured format, checking those values against document evidence, validating arithmetic and routing uncertain records to a human reviewer.

The hypothesis is testable with a pilot. The current project does not assume a particular volume of invoices, error rate, processing time, or savings at Cynbit or its clients.

## 4. Problem and user workflow

A typical invoice-intake workflow may require a staff member to:

1. Open a PDF or scanned invoice.
2. Read supplier, invoice identifier, dates, currency, line items, taxes, and total.
3. Enter those values in a spreadsheet or business system.
4. Check arithmetic and missing fields.
5. Search for an already-processed invoice.
6. Send exceptions for clarification or approval.

The repetitive extraction and initial checking steps are suitable for automation, while approval and exception handling should remain under human control.

## 5. Proposed solution: DocuFlow AI

DocuFlow AI provides five stages:

1. **Ingest:** accept PDF and common image formats.
2. **Read:** extract embedded PDF text or render scanned PDF pages and run OCR.
3. **Extract:** use a local LLM to produce structured invoice JSON, including supplier, invoice identifiers, dates, currency, totals, payment status, and line items.
4. **Verify:** check scalar fields against field-specific source labels and values; aggregate explicitly labelled CGST/SGST/IGST components where their sum matches the extracted tax amount; run business-rule checks; check duplicates.
5. **Review and export:** save in SQLite, allow human approval/rejection, support controlled evidence re-evaluation with an audit event, and export CSV/JSON.

## 6. Business value and measurable outcomes

Potential value areas include reducing repetitive keying, making missing or unsupported values visible earlier, standardising output fields, improving duplicate awareness, and retaining a review/audit trail.

A pilot should measure the following rather than assume benefits:

| Metric | Measurement approach |
|---|---|
| Field extraction accuracy | Correct extracted fields / total fields compared with manually labelled invoices |
| Evidence support rate | Populated fields with valid field-specific source evidence / populated fields |
| Human correction rate | Fields edited by a reviewer / fields extracted |
| Straight-through processing rate | Documents approved without manual field changes / documents processed |
| Processing time | Median time from upload to review-ready record |
| Duplicate detection precision | Correct duplicate alerts / all duplicate alerts |
| OCR failure rate | Scanned documents requiring re-upload or manual transcription / scanned documents |

No numeric ROI estimate is offered because there is no verified company document volume, baseline processing time, staffing cost, or error-rate dataset.

## 7. Risks and controls

| Risk | Proposed control |
|---|---|
| OCR misreads faint or joined text | Show source text/evidence; flag unsupported fields; human review |
| LLM invents or mislabels a field | Require structured output; validate with Pydantic; independently check evidence |
| Correct value appears in unrelated context | Use field-specific labels and context, not value-only matching |
| Tax components are incorrectly combined | Aggregate only explicitly labelled tax components and compare totals |
| Duplicate invoice is inserted | Check supplier + invoice number before insert |
| Approved record changes during re-evaluation | Update evidence metadata separately; preserve workflow status; append audit history |
| Sensitive documents are exposed | Keep processing local in this prototype; use synthetic examples; add production access/security controls before deployment |

## 8. Scope and boundaries

**Included in the proof of concept:** invoice upload, PDF text extraction, scanned-PDF/image OCR, local LLM extraction, structured validation, field-specific evidence indicators, basic arithmetic/date checks, duplicate detection, SQLite history, human approval, evidence re-evaluation audit, and CSV/JSON exports.

**Not included:** live integration with ERP/accounting software, bank/payment reconciliation, GST filing, signature authenticity, fraud detection, multi-tenant access control, production deployment, or validated performance on real customer invoice populations.

## 9. Recommendation

A limited pilot is recommended using a permissioned and representative invoice sample, manually labelled ground truth, and reviewer feedback. The pilot should establish accuracy and exception rates before any production integration. DocuFlow AI provides a demonstrable starting point for that evaluation and maps closely to Cynbit's publicly described LLM/document-processing focus.
