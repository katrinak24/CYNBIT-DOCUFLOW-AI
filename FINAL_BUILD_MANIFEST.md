# Final Build Manifest — Cynbit DocuFlow AI (Windows regression fix)

## Release contents
- Complete local-first Streamlit proof of concept.
- PDF text extraction and scanned-PDF OCR (PyMuPDF + Tesseract).
- Local Ollama/Qwen structured invoice extraction.
- Field-specific evidence checks, including multi-line CGST/SGST aggregation.
- Duplicate detection, human approval/rejection, and evidence re-evaluation audit history.
- CSV/JSON exports using one shared verification resolver and SQLite workflow status.
- Synthetic four-record SQLite database snapshot, scanned test invoice, expected output, and reference exports.
- AI Opportunity Report and Technical Approach Report (PDF and Markdown).

## Quality checks in this release
- `python -m pytest -q`: **46 passed**.
- `python -m compileall -q app.py core database utils`: passed.
- Bundled SQLite snapshot: 4 invoice records retained; 2 Approved, 2 Pending Review, 0 Rejected.
- CSV/JSON parity: invoice IDs, workflow statuses, and all four verification counts matched for all records.
- Export fallback: V3 records with confidence/evidence but no V4 verification map are derived correctly; legacy records with no verification metadata stay `Not evaluated`.

## Bundled database snapshot
- Record #4: Approved; 9/9 verified.
- Record #3: Pending Review; 8 verified, 1 needs review.
- Records #1 and #2: workflow statuses preserved; 9 fields each marked `Not evaluated` because those legacy records have no retained source text/evidence metadata.

## Windows runtime check
The full test suite was run in the build environment. The user's Windows run previously showed 43 passed / 3 failed; this release specifically fixes those three export-verification fallback cases and includes their regression tests. Please run `python -m pytest -v` after extracting this ZIP on Windows. Ollama and Tesseract remain local prerequisites.
