# Cynbit DocuFlow AI

**Local-first AI invoice extraction, field-specific evidence verification, financial validation, duplicate prevention, human approval, re-evaluation audit trail, and CSV/JSON export.**

This project is an assessment proof of concept designed around Cynbit's publicly described LLM automation and document-extraction work. It uses synthetic invoice examples and local inference; it is not a production accounting or tax system.

## 1. Main capabilities

- PDF text extraction and scanned-PDF OCR using PyMuPDF and Tesseract.
- PNG/JPG/TIFF image OCR.
- Structured invoice extraction through local Ollama (default model: `qwen2.5:3b`).
- Pydantic schema validation for invoice fields and line items.
- Field-specific evidence checks for vendor, invoice number, dates, currency, subtotal, tax, total, and payment status.
- Multi-line CGST/SGST/IGST aggregation when labelled tax components sum to the extracted tax amount.
- Duplicate detection using normalized vendor name + invoice number before database insertion.
- SQLite persistence and human approve/reject workflow.
- Reviewer corrections saved atomically with workflow status.
- Approval is blocked when required supplier/invoice/date/total fields are missing or populated scalar values lack field-specific evidence.
- Controlled evidence re-evaluation for an existing invoice. The selected source file is reprocessed; evidence metadata is updated while invoice business values and workflow status remain unchanged.
- Append-only verification audit events with source-file name, SHA-256 digest, before/after evidence state, timestamp, and preserved workflow status.
- CSV and JSON exports generated from one SQLite snapshot, with consistent verification summaries, v3 confidence/evidence fallback, and legacy `Not evaluated` handling.

## 2. Windows setup

Open PowerShell in the extracted project directory:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Tesseract OCR separately on Windows. The expected executable is commonly:

`C:\Program Files\Tesseract-OCR\tesseract.exe`

If the executable is installed but not on PATH, add it for the current PowerShell session:

```powershell
$env:Path += ";C:\Program Files\Tesseract-OCR"
```

Verify it:

```powershell
tesseract --version
tesseract --list-langs
python -c "import pymupdf, pytesseract; print('Python OCR dependencies OK')"
```

The `eng` language pack is required for the bundled synthetic invoice.

## 3. Ollama setup

Ollama must be running locally at `http://localhost:11434`. This build defaults to `qwen2.5:3b`.

```powershell
ollama list
ollama run qwen2.5:3b
```

If you prefer another installed model, set it before launch:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b-instruct"
```

Do not start a second `ollama serve` process if Ollama is already listening on port 11434.

## 4. Run automated tests

```powershell
python -m pytest -v
```

The bundled suite contains **46 automated tests** covering document validation, schema constraints, evidence matching, tax aggregation, duplicate lookups, SQLite migrations, approval persistence, export consistency, legacy status handling, and evidence re-evaluation audit behaviour.

The 46 tests passed in the final regression run for this release. Run them again on the target Windows machine before submitting.

## 5. Launch the application

```powershell
streamlit run app.py
```

Open `http://localhost:8501`.

## 6. Scanned PDF test

Upload `samples/invoices/DocuFlow_Scanned_Test_Invoice.pdf`. It is a synthetic image-only PDF with no selectable text layer. The extraction method should show `pdf_ocr`.

Expected invoice values:

| Field | Expected |
|---|---|
| Vendor | NORTHSTAR OFFICE SUPPLIES |
| Invoice number | NS-2026-1048 |
| Invoice date | 2026-10-30 |
| Due date | 2026-11-14 |
| Currency | INR |
| Subtotal | 8,000.00 |
| CGST | 720.00 |
| SGST | 720.00 |
| Combined tax | 1,440.00 |
| Grand total | 9,440.00 |
| Payment status | UNPAID |

## 7. Evidence re-evaluation

Open **History & exports → Evidence re-evaluation**. Select an existing invoice and upload its source PDF/image. Confirm that the selected file belongs to that record, then run re-evaluation.

The operation:

1. Re-extracts source text using the normal PDF/image pipeline.
2. Rechecks the stored invoice values against field-specific source evidence.
3. Updates only evidence metadata and the stored source text.
4. Leaves the invoice values and workflow status (`Pending Review`, `Approved`, or `Rejected`) unchanged.
5. Appends an audit row containing the original workflow status, source filename, hash, prior/new evidence state, and timestamp.

Do not upload an unrelated source file for a record. Re-evaluation is not an approval action.

## 8. Export semantics

- CSV and JSON use SQLite's workflow status as the single source of truth.
- Verification states are independent of workflow status.
- Records with no verification metadata are exported as `Not evaluated` (not `Needs review` and not `Verified`).
- Verification counts always reconcile to the 9 scalar fields tracked by this prototype.
- Re-evaluation events are included in JSON and summarized in CSV.

## 9. Known limitations and safety

- Confidence is not a calibrated probability. The displayed verification states indicate whether field-specific source evidence was found.
- A source-text match does not prove that an invoice is authentic, legally valid, or truthful.
- OCR may join nearby columns/labels, miss faint text, or misread characters. Human review remains mandatory.
- Tax aggregation is conservative and only sums explicitly labelled tax components.
- Duplicate matching uses vendor name + invoice number; production use would require stronger normalization and explicit exception handling.
- The local prototype has no multi-user authentication, role-based access control, encrypted secrets management, or production deployment controls.
- The bundled database contains synthetic test records. Do not commit confidential real invoices or local databases to a public repository.

## 10. Project structure

```text
CYNBIT_DOCUFLOW_AI/
├── app.py
├── config.py
├── requirements.txt
├── core/
│   ├── ai_extractor.py
│   ├── document_loader.py
│   ├── evidence.py
│   ├── schemas.py
│   ├── text_extractor.py
│   ├── validator.py
│   └── verification_summary.py
├── database/
│   ├── db.py
│   └── docuflow.db
├── utils/
│   └── export.py
├── samples/
│   ├── invoices/
│   └── expected_outputs/
├── tests/
├── assessment/
└── screenshots/
```

## 11. Cynbit public references

- Cynbit AI automation and services: https://www.cynbit.in/services
- AI/ML Engineer Intern role: https://www.cynbit.in/careers/ai-ml-engineer-intern
- Cynbit careers: https://www.cynbit.in/careers
- Cynbit homepage and product ecosystem: https://www.cynbit.in/

These public pages informed the problem/opportunity selection. No claim is made that Cynbit currently uses this prototype or has shared internal invoice data.
