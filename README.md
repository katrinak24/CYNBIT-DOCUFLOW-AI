# Cynbit DocuFlow AI

### AI-Powered Document Intelligence & Invoice Automation

**Extract. Verify. Validate. Approve.**

Cynbit DocuFlow AI is a local-first AI-powered document intelligence system that automates invoice processing using Large Language Models (LLMs), OCR, field-specific evidence verification and rule-based financial validation.

Built as a functional AI/ML engineering assessment proof of concept for the AI/ML Engineer Intern opportunity at Cynbit Technologies.

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)](https://streamlit.io/)
[![AI](https://img.shields.io/badge/AI-Ollama%20%7C%20Qwen2.5-green)](https://ollama.com/)
[![OCR](https://img.shields.io/badge/OCR-Tesseract-orange)](https://github.com/tesseract-ocr/tesseract)
[![Tests](https://img.shields.io/badge/Tests-46%20Passed-brightgreen)](#testing-and-quality-assurance)
[![License](https://img.shields.io/badge/Status-Assessment%20Prototype-blue)](#limitations-and-safety)

---

## 1. Project Overview

Businesses regularly receive invoices in different formats, including digital PDFs, scanned PDFs and images.

Manually processing these documents involves reading information, entering data, checking financial calculations, identifying duplicates and routing invoices for approval.

DocuFlow AI demonstrates how these repetitive activities can be automated using local AI models while retaining human control over financial decisions.

### Core capabilities

- Digital PDF text extraction.
- Scanned PDF and image OCR.
- LLM-powered structured invoice extraction.
- Supplier and invoice-field identification.
- Field-specific source evidence verification.
- CGST, SGST and IGST aggregation.
- Financial consistency validation.
- Duplicate invoice detection.
- Human approval and rejection workflow.
- Evidence re-evaluation with an audit trail.
- SQLite persistence.
- CSV and JSON exports.

## 2. Application Workflow

```text
          DOCUMENT UPLOAD
                 |
                 v
       DOCUMENT TYPE DETECTION
                 |
          +------+------+
          |             |
          v             v
      DIGITAL PDF    SCANNED PDF
          |             |
          v             v
       PyMuPDF       Tesseract OCR
          |             |
          +------+------+
                 |
                 v
          TEXT EXTRACTION
                 |
                 v
       LOCAL LLM EXTRACTION
        Ollama + Qwen2.5
                 |
                 v
       STRUCTURED JSON DATA
                 |
                 v
      EVIDENCE VERIFICATION
                 |
                 v
       FINANCIAL VALIDATION
                 |
                 v
       DUPLICATE DETECTION
                 |
                 v
         HUMAN REVIEW
                 |
          +------+------+
          |      |      |
          v      v      v
        APPROVE REJECT REVIEW
          |
          v
       SQLITE DATABASE
          |
          v
      CSV / JSON EXPORT
```

## 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python | Core application |
| Interface | Streamlit | Interactive web application |
| AI inference | Ollama | Local model execution |
| Language model | Qwen2.5 3B | Invoice information extraction |
| Digital PDF processing | PyMuPDF | PDF text extraction |
| OCR | Tesseract | Scanned-document recognition |
| Image processing | Pillow | Image loading and processing |
| Data validation | Pydantic | Structured data schemas |
| Database | SQLite | Invoice and audit persistence |
| Data processing | Pandas | Export and tabular operations |
| Testing | Pytest | Automated quality assurance |

## 4. Key Features

### A. Document Intelligence

Accepts:
- PDF documents.
- Scanned PDFs.
- PNG images.
- JPG/JPEG images.
- TIFF images.

The application automatically selects the appropriate extraction method:

- `pdf_text` for digitally generated PDFs.
- `pdf_ocr` for scanned PDFs.
- `image_ocr` for uploaded images.

### B. AI-Powered Invoice Extraction

Uses locally hosted Qwen2.5 through Ollama to extract structured invoice information.

Tracked fields include:

- Supplier/vendor name.
- Invoice number.
- Invoice date.
- Due date.
- Currency.
- Subtotal.
- Tax amount.
- Grand total.
- Payment status.
- Individual line items.

Extracted information is validated against a Pydantic schema.

### C. Field-Specific Evidence Verification

Every tracked scalar field is checked against the original extracted document text.

The verification system supports:

- Supplier identification.
- Label-specific invoice number matching.
- Date-context matching.
- Currency-context verification.
- Financial amount matching.
- Multi-line CGST and SGST aggregation.
- Grand-total verification.
- Payment-status verification.

Verification is reported independently from invoice approval status.

A source-text match does not prove that a document is authentic or truthful.

### D. Financial Validation

The validation engine checks:

- Missing required information.
- Subtotal and tax consistency.
- Invoice-total discrepancies.
- Date inconsistencies.
- Duplicate invoice records.

Tax aggregation supports explicitly labelled tax components when their amounts reconcile with the extracted tax total.

### E. Duplicate Detection

Uses normalized supplier name and invoice number to identify existing records before database insertion.

Duplicate uploads are prevented from creating additional invoice records.

### F. Human Approval Workflow

Reviewers can:

- Inspect extracted invoice information.
- Correct extracted JSON fields.
- Review field-level evidence.
- Approve invoices.
- Reject invoices.

Approval safeguards prevent approval when required fields are missing or populated fields lack the required supporting evidence.

Reviewer corrections and workflow status are saved together.

### G. Evidence Re-evaluation and Audit Trail

Existing invoices can be re-evaluated against their original source documents.

The system:
1. Reprocesses the selected source document.
2. Rechecks field-specific evidence.
3. Updates verification metadata.
4. Preserves invoice business values and approval status.
5. Records an append-only audit event.

### H. Data Management and Exports

SQLite is the application's single source of truth for workflow status.

Supported exports:

- CSV for tabular analysis.
- JSON for structured integration and downstream processing.

Both exports share consistent verification summaries and invoice workflow statuses.

Older records without verification information are identified as `Not evaluated`.

## 5. Windows Installation

### Prerequisites

- Windows 10/11.
- Python 3.14.
- Ollama.
- Tesseract OCR.
- Git.

### Step 1 — Clone the repository

```powershell
git clone https://github.com/katrinak24/CYNBIT-DOCUFLOW-AI.git

cd CYNBIT-DOCUFLOW-AI
```

### Step 2 — Create a virtual environment

```powershell
py -3.14 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate again.

### Step 3 — Install Python dependencies

```powershell
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

### Step 4 — Configure Tesseract OCR

Install Tesseract OCR for Windows.

Official Windows installer information:

https://github.com/UB-Mannheim/tesseract/wiki

The default executable location is commonly:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Add it to PATH for the current PowerShell session:

```powershell
$env:Path += ";C:\Program Files\Tesseract-OCR"
```

Verify:

```powershell
tesseract --version

tesseract --list-langs
```

The English language package (`eng`) is required for the bundled sample invoice.

### Step 5 — Configure Ollama

Install Ollama:

https://ollama.com/

Download the model:

```powershell
ollama pull qwen2.5:3b
```

Verify:

```powershell
ollama list
```

The application uses:

```text
http://localhost:11434
```

By default, the configured model is:

```text
qwen2.5:3b
```

To use another installed model:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b-instruct"
```

Ollama normally runs as a local service. Do not start another `ollama serve` process when the service is already listening on port 11434.

## 6. Run Automated Tests

Execute:

```powershell
python -m pytest -v
```

### Testing Results

**46 automated tests passed on Windows.**

The test suite covers:

| Testing area | Coverage |
|---|---|
| Document upload | File validation |
| AI schema | Structured data constraints |
| Evidence verification | Field-specific source matching |
| OCR evidence | Dates, values and text evidence |
| Tax aggregation | CGST/SGST reconciliation |
| Duplicate detection | Existing invoice lookup |
| Database | SQLite migrations and persistence |
| Approval workflow | Corrections and status management |
| Approval safeguards | Missing and unverified fields |
| CSV/JSON exports | Consistency and verification summaries |
| Legacy records | Not-evaluated handling |
| Audit history | Evidence re-evaluation |

Last verified test environment:

- Windows.
- Python 3.14.6.
- Pytest 9.2.0.
- 46 passed.
- 0 failed.

Run the suite locally to reproduce the results.

## 7. Launch the Application

Run:

```powershell
streamlit run app.py
```

Open:

http://localhost:8501

The application provides three primary sections:

1. **Process Document** — upload and extract invoice information.
2. **Review & Approve** — inspect, correct, approve or reject documents.
3. **History & Exports** — view invoice records and download CSV/JSON exports.

## 8. Sample Scanned Invoice

A synthetic image-only invoice is included:

```text
samples/invoices/DocuFlow_Scanned_Test_Invoice.pdf
```

It contains no selectable PDF text layer and is designed to exercise the Tesseract OCR pipeline.

Expected extraction method:

```text
pdf_ocr
```

### Expected values

| Field | Expected value |
|---|---|
| Vendor | NORTHSTAR OFFICE SUPPLIES |
| Invoice number | NS-2026-1048 |
| Invoice date | 2026-10-30 |
| Due date | 2026-11-14 |
| Currency | INR |
| Subtotal | ₹8,000.00 |
| CGST | ₹720.00 |
| SGST | ₹720.00 |
| Combined tax | ₹1,440.00 |
| Grand total | ₹9,440.00 |
| Payment status | UNPAID |

The bundled invoice is synthetic test data, not a real customer document.

## 9. Project Structure

```text
CYNBIT-DOCUFLOW-AI/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── BUILD_MANIFEST.md
├── .gitignore
├── .env.example
│
├── assessment/
│   ├── 01_AI_OPPORTUNITY_REPORT.pdf
│   ├── 01_AI_OPPORTUNITY_REPORT.md
│   ├── 02_TECHNICAL_APPROACH_REPORT.pdf
│   ├── 02_TECHNICAL_APPROACH_REPORT.md
│   └── 03_SUBMISSION_CHECKLIST.md
│
├── core/
│   ├── ai_extractor.py
│   ├── approval.py
│   ├── document_loader.py
│   ├── evidence.py
│   ├── schemas.py
│   ├── text_extractor.py
│   ├── validator.py
│   └── verification_summary.py
│
├── database/
│   └── db.py
│
├── samples/
│   ├── invoices/
│   ├── expected_outputs/
│   └── reference_exports/
│
├── screenshots/
│
├── tests/
│
└── utils/
    └── export.py
```

The SQLite database is created locally when the application initializes. It is not required to be committed to the public repository.

## 10. Configuration

Optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API address |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Local LLM model |
| `MAX_UPLOAD_MB` | 15 | Upload size limit |

Example:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"

$env:OLLAMA_URL = "http://localhost:11434"
```

## 11. Limitations and Safety

This project is an assessment proof of concept, not a production accounting or tax system.

Known limitations:

- LLM extraction can be incorrect or incomplete.
- OCR may misread characters or merge nearby text.
- Evidence verification establishes source-text support, not document authenticity.
- Verification indicators are not calibrated probability scores.
- Tax aggregation only handles supported, explicitly labelled components.
- Duplicate detection uses supplier name and invoice number.
- Production deployment would require authentication, authorization, stronger data protection, monitoring and integration testing.

Human review remains necessary before financial information is accepted.

Only synthetic or appropriately authorized documents should be used in public demonstrations.

## 12. Business Opportunity and Assessment Context

Cynbit DocuFlow AI explores an opportunity in business document automation: reducing repetitive invoice data entry and improving the traceability of extracted information.

The proposed system demonstrates a practical application of:

- Local Large Language Models.
- OCR and document processing.
- Structured AI extraction.
- Evidence-based verification.
- Rule-based financial validation.
- Human-in-the-loop automation.

The project was selected in response to publicly described Cynbit AI automation services and the document-extraction responsibilities in its AI/ML Engineer Intern opportunity.

### Public references

- Cynbit Services: https://www.cynbit.in/services
- AI/ML Engineer Intern: https://www.cynbit.in/careers/ai-ml-engineer-intern
- Cynbit Careers: https://www.cynbit.in/careers
- Cynbit Homepage: https://www.cynbit.in/

These references informed the opportunity selection. This prototype was independently developed using synthetic data. It does not use Cynbit internal documents or claim to be an existing Cynbit product.

---

## Author

**Katrina**

AI/ML Engineering Project | October 2026

GitHub: https://github.com/katrinak24/CYNBIT-DOCUFLOW-AI
