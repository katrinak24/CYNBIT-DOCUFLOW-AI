# DocuFlow AI v5 - Evidence Re-evaluation & Audit Consistency

## Release summary

This release closes the remaining verification/export consistency gap by adding explicit evidence re-evaluation for existing records.

## Changes

- Added `verification_summary` to the invoice schema and centralised summary/count calculation.
- Legacy records with no field-verification metadata are represented as `Not evaluated` across all nine tracked fields.
- CSV and JSON exports derive verification states/counts consistently and include the same SQLite workflow status.
- Added a `verification_audit` SQLite table.
- Added an evidence re-evaluation operation that updates only evidence metadata and source text; business values and workflow status are preserved.
- Added source SHA-256, source filename, timestamp, original workflow status, and previous/new verification metadata to the audit event.
- Added an Evidence re-evaluation section under History & exports.
- Approval gate blocks missing required fields and populated values without verified evidence.
- Added verification and re-evaluation information to the History view.
- Duplicate-processing status is shown separately from field-evidence status.
- Added regression tests for legacy counts, status preservation, append-only audit records, and export consistency.

## Bundled records

The four synthetic sample invoice records are retained with their workflow statuses:

| ID | Invoice | Workflow status | Verification at release build |
|---:|---|---|---|
| 4 | NS-2026-1048 | Approved | 9 Verified |
| 3 | NS-2026-1048 | Pending Review | 8 Verified, 1 Needs review |
| 2 | ABC-2026-001 | Pending Review | 9 Not evaluated |
| 1 | ABC-2026-001 | Approved | 9 Not evaluated |

The included test invoice source is available for records #3 and #4. The release build has re-evaluated those two records and created audit entries while preserving their Approved/Pending Review statuses. Older records #1 and #2 remain Not evaluated until their original source documents are supplied through the re-evaluation screen.

## Verification

- Automated tests: **46 passed** in the release build environment.
- Python compile check: passed.
- SQLite migration and data integrity smoke check: passed.
- Scanned test invoice OCR: previously exercised in the user's Windows environment with `pdf_ocr`; vendor, invoice number, date, due date, subtotal, combined tax, total, and payment status extracted.

Re-run `python -m pytest -v` on the target Windows machine and perform an Ollama/Tesseract smoke test before external submission.


## Windows regression compatibility fix
- Exports now derive field verification from v3 `field_confidence` + `field_evidence` metadata when a `field_verification` map is absent.
- Partial legacy evidence is labelled `Partially evaluated`; records with no verification metadata remain `Not evaluated`.
- CSV and JSON use the same resolver.
